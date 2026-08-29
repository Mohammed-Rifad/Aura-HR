from rest_framework import serializers
from .models import Conversation, Message, PendingAction
from .models import AIToolCall, Conversation, Message, PendingAction


class AIToolCallSerializer(serializers.ModelSerializer):
    """
    One thing the agent did, for the admin activity log.

    Note this exposes `arguments`, which includes the questions people asked.
    PendingActionSerializer deliberately hides the same field, because that
    one is sent to the user's own browser and the arguments must stay
    server-side. Different readers, different rules — an audit trail that
    hides what was attempted is not an audit trail.
    """

    class Meta:
        model = AIToolCall
        fields = [
            "id",
            "tool_name",
            "arguments",
            "actor_label",
            "allowed",
            "error",
            "duration_ms",
            "result_size",
            "created_at",
        ]


class ApprovalLogSerializer(serializers.ModelSerializer):
    """Every proposal the agent made, decided or not."""

    requested_by = serializers.EmailField(
        source="requested_by.email", read_only=True
    )
    decided_by = serializers.EmailField(
        source="decided_by.email", read_only=True, default=None
    )

    class Meta:
        model = PendingAction
        fields = [
            "id",
            "tool_name",
            "summary",
            "status",
            "requested_by",
            "decided_by",
            "decided_at",
            "error",
            "created_at",
        ]


class PendingActionSerializer(serializers.ModelSerializer):
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = PendingAction
        # tool_name and arguments are deliberately NOT here. The card shows
        # the summary; the arguments stay server-side so nothing the client
        # holds can be edited and sent back.
        fields = [
            "id", "summary", "status", "is_open",
            "expires_at", "decided_at", "created_at",
        ]


class DecisionSerializer(serializers.Serializer):
    """What the approve/reject buttons send — which is almost nothing."""

    note = serializers.CharField(
        required=False, allow_blank=True, max_length=500
    )

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """One turn, as the frontend needs it."""

    tool_calls = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "role", "text", "tool_calls", "created_at"]

    def get_tool_calls(self, obj):
        """
        Which tools this turn asked for.

        Day 16 shows these as live cards in the chat — "searching
        employees..." — which is what makes the agent feel transparent
        rather than magic.
        """
        return [
            {
                "name": part["function_call"]["name"],
                "args": part["function_call"].get("args", {}),
            }
            for part in obj.parts
            if "function_call" in part
        ]


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "updated_at"]


class ConversationDetailSerializer(ConversationSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ["messages"]


class ChatRequestSerializer(serializers.Serializer):
    """What the frontend sends."""

    # Leave out to start a new conversation.
    conversation = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(max_length=2000)
