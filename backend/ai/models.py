import uuid

from django.conf import settings
from django.db import models
from pgvector.django import VectorField
from datetime import timedelta
from django.utils import timezone

from common.models import BaseModel



class Conversation(BaseModel):
    """One chat thread between a person and the agent."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )

    # The first question, shortened. Gives the sidebar something to show
    # without loading every message.
    title = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self):
        return self.title or f"Conversation {self.pk}"


class Message(BaseModel):
    """
    One turn in a conversation.

    Append-only, like AuditLog. A message is a record of what was said —
    editing one would make the transcript a lie.
    """

    class Role(models.TextChoices):
        # Gemini's own words. "model" where other APIs say "assistant".
        USER = "user", "User"
        MODEL = "model", "Model"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )

    role = models.CharField(max_length=10, choices=Role.choices)

    # What a human reads. Empty when the turn was only a tool call.
    text = models.TextField(blank=True)

    # Exactly what the API needs to replay this turn — text, function calls,
    # and function results. Stored raw so rebuilding the conversation is a
    # copy, not a reconstruction.
    parts = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["conversation", "created_at"])]

    def __str__(self):
        return f"{self.role}: {self.text[:40]}"

class AIToolCall(models.Model):
    """
    One tool invocation by the agent.

    Append-only, like AuditLog. This is the record of what the AI *did* —
    separate from the conversation, which is what a person *said*.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="tool_calls",
        null=True,
        blank=True,
    )

    # Who the tool ran AS. Not "who owns the chat" — the two are the same
    # today, but on Day 15 an approved action runs later, and this stays
    # the person whose permissions were used.
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_tool_calls",
    )
    actor_label = models.CharField(max_length=255, blank=True)

    tool_name = models.CharField(max_length=100, db_index=True)
    arguments = models.JSONField(default=dict, blank=True)

    # False when the tool refused — no permission, or unknown tool.
    allowed = models.BooleanField(default=True, db_index=True)
    error = models.TextField(blank=True)

    # How long it took, and how much came back. Both are useful signals:
    # a slow tool hurts the chat, and a huge result floods the context.
    duration_ms = models.PositiveIntegerField(default=0)
    result_size = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tool_name", "-created_at"]),
            models.Index(fields=["actor", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.tool_name} by {self.actor_label}"



class KnowledgeDocument(BaseModel):
    """
    A document the assistant is allowed to read.

    employee is null  → company-wide, everyone may read it
    employee is set   → personal, readable only by people who can already
                        see that employee
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="knowledge/%Y/%m/")

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="knowledge_documents",
        help_text="Leave empty for a company-wide document.",
    )

    is_active = models.BooleanField(default=True)
    chunk_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    """
    One searchable piece of a document.

    Documents are split up because you want to send the model the three
    relevant paragraphs, not the whole handbook.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    document = models.ForeignKey(
        KnowledgeDocument, on_delete=models.CASCADE, related_name="chunks"
    )

    # Copied from the document on purpose. The permission filter runs inside
    # the search query, and a plain column is far cheaper to filter on than
    # a join — this is the column that keeps other people's documents out.
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="document_chunks",
    )

    chunk_index = models.PositiveIntegerField()
    content = models.TextField()

    # 768 numbers describing what this chunk MEANS. Produced by
    # gemini-embedding-2. Change the model and every row must be rebuilt —
    # vectors from different models are not comparable.
    embedding = VectorField(dimensions=768)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["document", "chunk_index"]
        indexes = [models.Index(fields=["employee"])]

    def __str__(self):
        return f"{self.document.title} #{self.chunk_index}"


# How long a proposal stays clickable. Short on purpose: an approval you
# forgot about for an hour is an approval you are no longer thinking about,
# and the world may have moved on. Expired ones are simply asked again.
APPROVAL_WINDOW = timedelta(minutes=15)


class PendingAction(BaseModel):
    """
    Something the agent wants to do, waiting for a person to say yes.

    The agent proposes in one HTTP request and a human decides in another.
    Nothing survives between two requests except the database, so everything
    needed to run the action later — and to judge whether it still should be
    run — is written down here.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Waiting for a decision"
        APPROVED = "APPROVED", "Approved and done"
        REJECTED = "REJECTED", "Rejected"
        EXPIRED = "EXPIRED", "Expired before anyone decided"
        FAILED = "FAILED", "Approved but the action failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="pending_actions",
    )

    # What to run, and with what. Read back from HERE when the button is
    # clicked — never from the request body. The browser only ever sends the
    # id of this row, so it cannot swap the arguments for different ones.
    tool_name = models.CharField(max_length=100, db_index=True)
    arguments = models.JSONField(default=dict, blank=True)

    # The sentence shown on the confirmation card: "Approve 5 days annual
    # leave for Robert Johnson, 3–7 September". Written when the action is
    # proposed, because the person deciding must see what they are deciding
    # in plain words, not a tool name and a UUID.
    summary = models.CharField(max_length=300)

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_actions_requested",
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Recorded separately from requested_by. Usually the same person, but
    # not necessarily — and "who actually authorised this" is the question
    # an auditor asks.
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_actions_decided",
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    # What the tool returned, or why it blew up. Kept so the conversation can
    # be told the outcome, and so a failed approval is visible afterwards
    # rather than looking like it never happened.
    result = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)

    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["conversation", "status"])]

    def __str__(self):
        return f"{self.tool_name} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + APPROVAL_WINDOW
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        """Can this still be decided?"""
        return self.status == self.Status.PENDING and timezone.now() < self.expires_at
