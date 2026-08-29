"""
Business logic for attendance.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone

from audit.models import AuditLog
from audit.services import log_action
from leave.models import LeaveRequest

from .models import Attendance

FULL_DAY_HOURS = Decimal("8")


def _today():
    """
    The local calendar date.

    localdate(), NOT now().date(). now() is UTC. At 2am in Dubai it is still
    the previous day in UTC, and the record would land on the wrong day.
    """
    return timezone.localdate()


def _on_approved_leave(employee, day):
    """True if an approved leave request covers this date."""
    return LeaveRequest.objects.filter(
        employee=employee,
        status=LeaveRequest.Status.APPROVED,
        start_date__lte=day,
        end_date__gte=day,
    ).exists()


@transaction.atomic
def check_in(*, employee, actor=None):
    """Start the working day."""
    today = _today()

    if _on_approved_leave(employee, today):
        raise ValidationError("You are on approved leave today.")

    record, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today,
        defaults={"check_in": timezone.now(), "created_by": actor},
    )

    if not created:
        if record.check_in:
            local = timezone.localtime(record.check_in)
            raise ValidationError(f"Already checked in today at {local:%H:%M}.")
        record.check_in = timezone.now()
        record.save(update_fields=["check_in", "updated_at"])

    log_action(action=AuditLog.Action.CREATE, instance=record, actor=actor)
    return record


@transaction.atomic
def check_out(*, employee, actor=None):
    """End the working day and record the hours."""
    today = _today()

    try:
        record = Attendance.objects.select_for_update().get(
            employee=employee, date=today
        )
    except Attendance.DoesNotExist:
        raise ValidationError("You have not checked in today.")

    if record.check_in is None:
        raise ValidationError("You have not checked in today.")

    if record.check_out is not None:
        local = timezone.localtime(record.check_out)
        raise ValidationError(f"Already checked out today at {local:%H:%M}.")

    now = timezone.now()

    # Subtracting two timestamps handles overnight shifts correctly.
    # In at 10pm, out at 6am -> 8 hours, not minus 16.
    hours = Decimal((now - record.check_in).total_seconds()) / Decimal(3600)

    record.check_out = now
    record.work_hours = hours.quantize(Decimal("0.01"))
    record.status = (
        Attendance.Status.PRESENT
        if record.work_hours >= FULL_DAY_HOURS
        else Attendance.Status.HALF_DAY
    )
    record.updated_by = actor
    record.save(
        update_fields=["check_out", "work_hours", "status", "updated_by", "updated_at"]
    )

    log_action(
        action=AuditLog.Action.UPDATE,
        instance=record,
        actor=actor,
        changes={"work_hours": {"before": "0", "after": str(record.work_hours)}},
    )
    return record


def monthly_summary(employee, year, month):
    """One month, counted. Two queries, not one per day."""
    records = Attendance.objects.filter(
        employee=employee, date__year=year, date__month=month
    )

    totals = records.aggregate(
        days_recorded=Count("id"),
        total_hours=Sum("work_hours"),
    )

    by_status = {
        row["status"]: row["n"]
        for row in records.values("status").annotate(n=Count("id"))
    }

    return {
        "year": year,
        "month": month,
        "days_recorded": totals["days_recorded"] or 0,
        "total_hours": totals["total_hours"] or Decimal("0"),
        "present": by_status.get(Attendance.Status.PRESENT, 0),
        "half_day": by_status.get(Attendance.Status.HALF_DAY, 0),
        "absent": by_status.get(Attendance.Status.ABSENT, 0),
        "on_leave": by_status.get(Attendance.Status.ON_LEAVE, 0),
    }
