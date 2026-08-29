import uuid

from django.conf import settings
from django.db import models

class AuditLog(models.Model):
    """
    An append-only record of every meaningful change.

    Deliberately NOT a BaseModel. No updated_at, no updated_by, no soft
    delete — a log you can edit is not a log. Rows are written once and
    never touched again.
    """

    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        APPROVE = "APPROVE", "Approve"
        REJECT = "REJECT", "Reject"
        CANCEL = "CANCEL", "Cancel"
        LOGIN = "LOGIN", "Login"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # SET_NULL, never CASCADE. Deleting a user must not erase the history of
    # what they did.
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    # The actor's email, copied at write time. If the user row is ever
    # removed, actor goes null but this still says who it was.
    actor_label = models.CharField(max_length=255, blank=True)

    action = models.CharField(
        max_length=20, choices=Action.choices, db_index=True
    )

    # Text, not a ForeignKey: this table points at every model in the
    # project. Django's ContentType framework does this properly, but adds a
    # join to every read for little gain here.
    model_name = models.CharField(max_length=100, db_index=True)
    object_id = models.CharField(max_length=64, db_index=True)
    # str(instance) at write time, so the log is readable without joining
    # back to a row that may no longer exist.
    object_label = models.CharField(max_length=255, blank=True)

    # {"status": {"before": "PENDING", "after": "APPROVED"}}
    changes = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # "everything that happened to this object"
            models.Index(fields=["model_name", "object_id", "-created_at"]),
            # "everything this person did"
            models.Index(fields=["actor", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.action} {self.model_name} {self.object_id}"
