"""
The data the suite assumes exists.

Run before an evaluation. Without fixed data, scores move for reasons
unrelated to the agent, and a regression is indistinguishable from someone
having approved a request last Tuesday.
"""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from employees.models import Employee
from leave.models import LeaveRequest, LeaveType
from leave.services import apply_leave

# The employee every gate case names.
SUBJECT = "ENG1106"


def ensure_pending_request():
    """Make sure the subject has exactly one pending leave request."""
    employee = Employee.objects.get(employee_id=SUBJECT)

    existing = LeaveRequest.objects.filter(
        employee=employee, status=LeaveRequest.Status.PENDING
    ).first()
    if existing:
        return existing

    leave_type = LeaveType.objects.get(code="ANNUAL")

    # Walk forward until a free window turns up — apply_leave rejects past
    # dates and overlaps with earlier runs.
    start = timezone.localdate() + timedelta(days=45)
    for _ in range(12):
        while start.weekday() >= 5:
            start += timedelta(days=1)
        try:
            return apply_leave(
                employee=employee,
                leave_type=leave_type,
                start_date=start,
                end_date=start + timedelta(days=2),
                reason="Fixture for the evaluation suite",
            )
        except ValidationError:
            start += timedelta(days=14)

    raise RuntimeError("No free window for the fixture request.")


def prepare():
    """Everything the suite needs in place."""
    return {"pending_request": ensure_pending_request()}
