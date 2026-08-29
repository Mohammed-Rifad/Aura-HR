from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from employees.models import Employee

from .models import Attendance
from .serializers import AttendanceSerializer, MonthlySummarySerializer
# Aliased so the action methods below can share the same names without
# reading like they call themselves.
from .services import check_in as do_check_in
from .services import check_out as do_check_out
from .services import monthly_summary


def _visible_attendance(user):
    """
    Attendance rows this user may see. None means no filter (Admin and HR).

    Deliberately not keyed on role == MANAGER. Who manages whom is a fact
    recorded in Employee.manager; the role flag is a separate field that
    drifts out of sync with it.
    """
    Roles = user.Roles
    if user.role in (Roles.ADMIN, Roles.HR):
        return None
    return Q(employee__user=user) | Q(employee__manager__user=user)


def _visible_employees(user):
    """The same rule, expressed against Employee rather than Attendance."""
    Roles = user.Roles
    if user.role in (Roles.ADMIN, Roles.HR):
        return None
    return Q(user=user) | Q(manager__user=user)


class AttendanceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Read attendance. Check in and out.

    No create, no update, no destroy. Rows are written by the service, from
    the two actions below — never by a plain POST or PATCH.
    """

    queryset = Attendance.objects.none()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    # A dict, not a list: "date" alone would only allow an exact match, so a
    # month view (?date__gte=...&date__lte=...) would be impossible.
    filterset_fields = {
        "date": ["exact", "gte", "lte"],
        "status": ["exact"],
        "employee": ["exact"],
    }

    def get_queryset(self):
        qs = Attendance.objects.select_related("employee__user")
        scope = _visible_attendance(self.request.user)
        return qs if scope is None else qs.filter(scope)

    def _my_employee(self):
        employee = getattr(self.request.user, "employee", None)
        if employee is None:
            raise ValidationError(
                "Your account has no employee record, so you cannot check in."
            )
        return employee

    def _target_employee(self):
        """
        Whose attendance a read action is about.

        Defaults to the caller. An explicit ?employee=<id> is honoured only if
        that person is inside the caller's scope — the same rule that governs
        the list governs the summary, so there is no second way in.
        """
        employee_id = self.request.query_params.get("employee")
        if not employee_id:
            return self._my_employee()

        employees = Employee.objects.all()
        scope = _visible_employees(self.request.user)
        if scope is not None:
            employees = employees.filter(scope)

        try:
            employee = employees.filter(pk=employee_id).first()
        except (DjangoValidationError, ValueError):
            # Not a UUID at all. Same answer as "not yours" — never confirm
            # whether an id exists.
            employee = None

        if employee is None:
            raise NotFound("No such employee.")
        return employee

    @action(detail=False, methods=["post"], url_path="check-in")
    def check_in(self, request):
        record = do_check_in(employee=self._my_employee(), actor=request.user)
        return Response(
            AttendanceSerializer(record).data, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"], url_path="check-out")
    def check_out(self, request):
        record = do_check_out(employee=self._my_employee(), actor=request.user)
        return Response(AttendanceSerializer(record).data)

    @action(detail=False, methods=["get"])
    def today(self, request):
        record = (
            self.get_queryset()
            .filter(employee=self._target_employee(), date=timezone.localdate())
            .first()
        )
        if record is None:
            return Response(
                {"detail": "No attendance record for today."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(AttendanceSerializer(record).data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        One month, counted. Defaults to the caller and the current month.

        ?employee=<id> lets a manager see a report and HR see anyone, scoped
        by _target_employee().
        """
        today = timezone.localdate()
        try:
            year = int(request.query_params.get("year", today.year))
            month = int(request.query_params.get("month", today.month))
        except (TypeError, ValueError):
            raise ValidationError("year and month must be numbers.")

        if not 1 <= month <= 12:
            raise ValidationError("month must be between 1 and 12.")

        data = monthly_summary(self._target_employee(), year, month)
        return Response(MonthlySummarySerializer(data).data)
