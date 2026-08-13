from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import LeaveBalance, LeaveRequest, LeaveType
from .serializers import (
    LeaveBalanceSerializer,
    LeaveDecisionSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestDetailSerializer,
    LeaveRequestListSerializer,
    LeaveTypeSerializer,
)
from .services import approve_leave, cancel_leave, reject_leave


def _visible_to(user):
    """
    The rows this user may see, as a filter fragment.

    HR and Admin see everything. Everyone else sees their own records plus
    those of anyone reporting to them. Not keyed on role == MANAGER — the
    org chart in Employee.manager is the fact.
    """
    Roles = user.Roles
    if user.role in (Roles.ADMIN, Roles.HR):
        return None  # no filter
    return Q(employee__user=user) | Q(employee__manager__user=user)


class LeaveTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Reference data. Everyone reads it; HR edits it in the admin."""

    queryset = LeaveType.objects.filter(is_active=True)
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]


class LeaveBalanceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List only. Balances are changed by the service, never by a request."""

    queryset = LeaveBalance.objects.none()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["year", "leave_type", "employee"]

    def get_queryset(self):
        qs = LeaveBalance.objects.select_related("leave_type", "employee__user")
        scope = _visible_to(self.request.user)
        return qs if scope is None else qs.filter(scope)


class LeaveRequestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Apply for leave, view requests, decide them.

    No update, no destroy. A leave request is never edited — it moves
    through statuses. Cancelling is an action, not a DELETE, because it has
    to release the balance hold as well as change the status.
    """

    queryset = LeaveRequest.objects.none()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "leave_type", "employee"]
    ordering_fields = ["start_date", "created_at", "status"]

    def get_queryset(self):
        qs = LeaveRequest.objects.select_related(
            "employee__user",
            "employee__department",
            "employee__designation",
            "leave_type",
            "approver",
        )
        scope = _visible_to(self.request.user)
        return qs if scope is None else qs.filter(scope)

    def get_serializer_class(self):
        if self.action == "create":
            return LeaveRequestCreateSerializer
        if self.action in ("approve", "reject"):
            return LeaveDecisionSerializer
        if self.action == "list":
            return LeaveRequestListSerializer
        return LeaveRequestDetailSerializer

    def _detail(self, leave_request, code=status.HTTP_200_OK):
        """Every write responds with the full object, not the input fields."""
        return Response(
            LeaveRequestDetailSerializer(
                leave_request, context=self.get_serializer_context()
            ).data,
            status=code,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._detail(serializer.save(), status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._detail(
            approve_leave(
                leave_request=self.get_object(),
                approver=request.user,
                note=serializer.validated_data["note"],
            )
        )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._detail(
            reject_leave(
                leave_request=self.get_object(),
                approver=request.user,
                note=serializer.validated_data["note"],
            )
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        return self._detail(
            cancel_leave(leave_request=self.get_object(), actor=request.user)
        )
