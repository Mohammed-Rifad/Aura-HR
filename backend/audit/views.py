from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsAdmin

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Who changed what, when, and from where.

    List and retrieve only — deliberately not a ModelViewSet. The model
    already refuses add, change and delete in the Django admin; leaving a
    write path open through the API would make that pointless. An audit log
    you can edit is not evidence of anything.
    """

    queryset = AuditLog.objects.select_related("actor").order_by("-created_at")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    filterset_fields = ["action", "model_name", "actor"]
    search_fields = ["actor_label", "object_label", "object_id"]
    ordering_fields = ["created_at"]

    @action(detail=False)
    def models(self, request):
        """
        The model names that actually appear in the log.

        Fills the filter dropdown with what exists rather than a hardcoded
        list that drifts every time a new model starts being audited.
        """

        return Response(
            sorted(
                AuditLog.objects
                # order_by() with no arguments clears Meta.ordering. Without
                # it Django adds created_at to the SELECT for the ORDER BY,
                # every row has a unique timestamp, and distinct() returns
                # everything.
                .order_by()
                .values_list("model_name", flat=True)
                .distinct()
            )
        )

