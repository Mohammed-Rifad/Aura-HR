from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(
        source="get_action_display", read_only=True
    )

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "action",
            "action_display",
            "model_name",
            "object_id",
            "object_label",
            "actor_label",
            "changes",
            "ip_address",
            "created_at",
        ]
        # Every field, always. There is no write path to this model — see
        # the viewset.
        read_only_fields = fields
