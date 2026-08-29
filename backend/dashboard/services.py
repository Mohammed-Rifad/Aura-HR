"""
Read-only aggregates for the dashboard.

Also the source for the AI agent's analytics tools on Day 13 — which is why
this is a service and not a view. Both callers get the same numbers and the
same scoping.
"""

from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from common.scoping import visible_employees
from employees.models import Employee, EmployeeDocument
from leave.models import LeaveBalance, LeaveRequest

EXPIRY_WINDOW_DAYS = 30


def headcount_by_department(user):
    """Active headcount per department, scoped to what this user may see."""
    rows = (
        visible_employees(user)
        .filter(status=Employee.Status.ACTIVE)
        .values("department__code", "department__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return [
        {
            "code": row["department__code"],
            "name": row["department__name"],
            "count": row["count"],
        }
        for row in rows
    ]


def pending_approvals(user):
    """
    Leave requests this user could actually decide.

    Their own request is excluded — nobody approves their own, so it does not
    belong in their inbox.
    """
    queryset = LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING)

    Roles = user.Roles
    if user.role not in (Roles.ADMIN, Roles.HR):
        queryset = queryset.filter(employee__manager__user=user)

    return queryset.exclude(employee__user=user)


def expiring_documents(user, days=EXPIRY_WINDOW_DAYS):
    """Documents expiring within `days`, plus any already expired."""
    today = timezone.localdate()
    return EmployeeDocument.objects.filter(
        employee__in=visible_employees(user),
        expiry_date__lte=today + timedelta(days=days),
    ).select_related("employee__user").order_by("expiry_date")


def on_leave_today(user):
    today = timezone.localdate()
    return LeaveRequest.objects.filter(
        employee__in=visible_employees(user),
        status=LeaveRequest.Status.APPROVED,
        start_date__lte=today,
        end_date__gte=today,
    ).count()


def my_balances(user):
    """The caller's own leave balances for this year."""
    employee = getattr(user, "employee", None)
    if employee is None:
        return []

    rows = LeaveBalance.objects.filter(
        employee=employee, year=timezone.localdate().year
    ).select_related("leave_type")

    return [
        {
            "code": row.leave_type.code,
            "name": row.leave_type.name,
            "allocated": str(row.allocated),
            "used": str(row.used),
            "available": str(row.available),
        }
        for row in rows
    ]


def summary(user):
    """Everything the dashboard needs, in one response."""
    employees = visible_employees(user)

    return {
        "headcount": employees.filter(status=Employee.Status.ACTIVE).count(),
        "headcount_total": employees.count(),
        "by_department": headcount_by_department(user),
        "pending_approvals": pending_approvals(user).count(),
        "expiring_documents": expiring_documents(user).count(),
        "on_leave_today": on_leave_today(user),
        "my_balances": my_balances(user),
        "expiring_soon": expiring_documents_list(user),
        "awaiting_approval": pending_approvals_list(user),

    }


def expiring_documents_list(user, limit=5):
    """The soonest-expiring documents, already-expired first."""
    today = timezone.localdate()

    return [
        {
            "id": str(document.id),
            "employee_id": document.employee.employee_id,
            "employee_name": (
                document.employee.user.get_full_name()
                or document.employee.user.email
            ),
            "document_type": document.get_document_type_display(),
            "expiry_date": document.expiry_date.isoformat(),
            "days_left": (document.expiry_date - today).days,
        }
        for document in expiring_documents(user)[:limit]
    ]


def pending_approvals_list(user, limit=5):
    """The leave requests this user could decide, soonest start first."""
    rows = (
        pending_approvals(user)
        .select_related("employee__user", "leave_type")
        .order_by("start_date")[:limit]
    )

    return [
        {
            "id": str(request.id),
            "employee_name": (
                request.employee.user.get_full_name()
                or request.employee.user.email
            ),
            "leave_type": request.leave_type.code,
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "days": str(request.days),
        }
        for request in rows
    ]
