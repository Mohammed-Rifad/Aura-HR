import logging
import json

from django.http import StreamingHttpResponse

from .services import ask, ask_stream, decide

from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework import generics, mixins, status, viewsets
from .models import Conversation
from .serializers import (
    ChatRequestSerializer,
    ConversationDetailSerializer,
    ConversationSerializer,
)
from .services import ask
from rest_framework.decorators import action as drf_action

from .models import Conversation, PendingAction
from .serializers import (
    ChatRequestSerializer,
    ConversationDetailSerializer,
    ConversationSerializer,
    DecisionSerializer,
    PendingActionSerializer,
)
from .services import ask, decide

logger = logging.getLogger(__name__)


def _sse(payload):
    """
    One Server-Sent Event.

    The trailing blank line is the delimiter, not formatting. Without it the
    browser waits forever for the event to end.
    """
    return f"data: {json.dumps(payload)}\n\n"

class ChatView(generics.GenericAPIView):

    """
    POST a question, get an answer.

    Throttled hard. One question is several requests to the AI provider,
    and the free tier allows 500 a day — a curious visitor should not be
    able to drain it.
    """
    serializer_class = ChatRequestSerializer 
    permission_classes = [IsAuthenticated]
    throttle_scope = "ai"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data) 
        # serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_id = serializer.validated_data.get("conversation")

        if conversation_id:
            # Scoped to the caller. You cannot continue someone else's chat.
            conversation = Conversation.objects.filter(
                id=conversation_id, user=request.user
            ).first()
            if conversation is None:
                return Response(
                    {"detail": "Conversation not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            conversation = Conversation.objects.create(user=request.user)

        try:
            answer = ask(
                conversation=conversation,
                question=serializer.validated_data["message"],
                user=request.user,
            )
        except Exception:
            # Provider outage, rate limit, bad key. Log the detail, tell the
            # user something human.
            logger.exception("Agent failed for conversation %s", conversation.pk)
            return Response(
                {"detail": "The assistant is unavailable right now. Try again shortly."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        conversation.refresh_from_db()

        return Response(
            {
                "conversation": str(conversation.id),
                "title": conversation.title,
                "answer": answer,
                "pending_action": (
                    PendingActionSerializer(pending).data if pending else None
                ),
            }
        )

class ChatStreamView(generics.GenericAPIView):
    """
    The same question as /chat/, answered live.

    Holds one connection open and writes an event down it each time the
    agent does something, so the user watches it work instead of watching
    a spinner.
    """

    serializer_class = ChatRequestSerializer
    permission_classes = [IsAuthenticated]
    throttle_scope = "ai"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_id = serializer.validated_data.get("conversation")
        if conversation_id:
            conversation = Conversation.objects.filter(
                id=conversation_id, user=request.user
            ).first()
            if conversation is None:
                return Response(
                    {"detail": "Conversation not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            conversation = Conversation.objects.create(user=request.user)

        # Pulled out of `request` deliberately. The generator below runs
        # AFTER this method returns, and reaching into request from there is
        # how you get confusing bugs later.
        question = serializer.validated_data["message"]
        user = request.user

        def events():
            # Sent straight away so the browser knows the connection is
            # alive, and gets the conversation id before anything else.
            yield _sse({"type": "start", "conversation": str(conversation.id)})

            try:
                for event in ask_stream(
                    conversation=conversation, question=question, user=user
                ):
                    yield _sse(event)
            except Exception:
                # The 200 status line went out several seconds ago, so a 500
                # is no longer possible. The only way left to report a
                # failure is as another event.
                logger.exception("Stream failed for conversation %s", conversation.pk)
                yield _sse({
                    "type": "error",
                    "message": "The assistant stopped unexpectedly. Please try again.",
                })

            conversation.refresh_from_db()
            yield _sse({"type": "done", "title": conversation.title})

        response = StreamingHttpResponse(
            events(), content_type="text/event-stream"
        )
        # Proxies buffer responses by default, which would hold every event
        # until the end and undo the entire point of this view.
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response

class ConversationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Your own chats. No create — starting one is what /chat/ does."""

    queryset = Conversation.objects.none()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Not role-scoped like the rest of the app. A conversation belongs to
        # exactly one person — not even HR reads someone else's chat.
        return Conversation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConversationDetailSerializer
        return ConversationSerializer


class PendingActionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Things the agent wants to do, waiting on a person.

    The agent proposed these in an earlier request. Nothing here has
    happened yet.
    """

    queryset = PendingAction.objects.none()
    serializer_class = PendingActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Your own conversations only. Same rule as ConversationViewSet —
        # not even HR decides on someone else's chat.
        return PendingAction.objects.filter(conversation__user=self.request.user)

    @drf_action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._decide(request, pk, approve=True)

    @drf_action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._decide(request, pk, approve=False)

    def _decide(self, request, pk, *, approve):
        serializer = DecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Only the id and the yes/no reach the service. Deliberately no way
        # for the request body to influence WHAT runs.
        action, answer = decide(
            action_id=pk,
            user=request.user,
            approve=approve,
            note=serializer.validated_data.get("note", ""),
        )

        return Response(
            {
                "action": PendingActionSerializer(action).data,
                "answer": answer,
            }
        )
from django.db.models import Count

from common.permissions import IsAdmin

from .models import AIToolCall, Conversation, PendingAction
from .serializers import (
    AIToolCallSerializer,
    ApprovalLogSerializer,
    ChatRequestSerializer,
    ConversationDetailSerializer,
    ConversationSerializer,
    DecisionSerializer,
    PendingActionSerializer,
)
class AIActivityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Every tool the agent has ever run, successful or refused.

    Admin only. This is the answer to "how do you know what the AI did" —
    and the refused rows matter as much as the successful ones, because they
    are the record of the scoping rules actually firing.
    """

    queryset = AIToolCall.objects.select_related("actor").order_by("-created_at")
    serializer_class = AIToolCallSerializer
    permission_classes = [IsAdmin]

    filterset_fields = ["tool_name", "allowed"]
    search_fields = ["actor_label", "tool_name", "error"]
    ordering_fields = ["created_at", "duration_ms"]

    @drf_action(detail=False)
    def summary(self, request):
        """Counts for the page header. Respects the same filters as the list."""
        queryset = self.filter_queryset(self.get_queryset())

        return Response(
            {
                "total": queryset.count(),
                "refused": queryset.filter(allowed=False).count(),
                "by_tool": list(
                    queryset.values("tool_name")
                    .annotate(count=Count("id"))
                    .order_by("-count")[:10]
                ),
                "awaiting_approval": PendingAction.objects.filter(
                    status=PendingAction.Status.PENDING
                ).count(),
            }
        )


class ApprovalLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Every write the agent proposed, and what a human decided.

    Separate from AIActivityViewSet on purpose. A tool call records what RAN;
    this records what was ASKED FOR. A proposal that was never approved never
    ran, so it appears here and nowhere else — and "what did it try to do
    that we said no to" is the more interesting question.
    """

    queryset = (
        PendingAction.objects.select_related("requested_by", "decided_by")
        .order_by("-created_at")
    )
    serializer_class = ApprovalLogSerializer
    permission_classes = [IsAdmin]

    filterset_fields = ["status", "tool_name"]
    ordering_fields = ["created_at", "decided_at"]
