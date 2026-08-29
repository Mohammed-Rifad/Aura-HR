"""
Business logic for leave.

Every write goes through here — the API, the admin, and on Day 13 the AI
agent. Balance arithmetic only stays correct if exactly one place performs it.
"""

from datetime import timedelta
from decimal import Decimal
from audit.models import AuditLog
from audit.services import diff, log_action, snapshot
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone
from .models import LeaveBalance, LeaveRequest

WEEKEND = {5, 6}  # Saturday, Sunday — weekday() is 0=Monday


def working_days(start_date, end_date):
    """
    Working days between two dates, inclusive of both ends.

    NOT (end - start).days. That is wrong twice: it is off by one (Monday to
    Monday is 1 day, not 0), and it counts weekends (Friday to Monday is 2
    working days, not 4).

    Known limitation: public holidays are not excluded. That needs a Holiday
    model and a country calendar.
    """
    if end_date < start_date:
        raise ValidationError("End date cannot be before the start date.")

    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() not in WEEKEND:
            days += 1
        current += timedelta(days=1)

    return Decimal(days)


def get_balance(employee, leave_type, year=None, lock=False):
    """
    The balance row for one employee, type, and year.

    lock=True issues SELECT ... FOR UPDATE, which holds the row until the
    surrounding transaction commits. Required before changing the numbers:
    without it, two simultaneous requests both read pending=0, both write
    pending=5, and one request's hold silently disappears.
    """
    year = year or timezone.localdate().year

    manager = LeaveBalance.objects.select_for_update() if lock else LeaveBalance.objects

    try:
        return manager.get(employee=employee, leave_type=leave_type, year=year)
    except LeaveBalance.DoesNotExist:
        raise ValidationError(
            f"No {leave_type.code} balance allocated for {year}."
        )


def _overlapping_requests(employee, start_date, end_date, exclude_pk=None):
    """
    Existing requests that clash with this range.

    Two ranges overlap unless one ends before the other begins:
        new_start <= existing_end  AND  new_end >= existing_start

    Only PENDING and APPROVED block. A rejected or cancelled request is not
    holding any dates.
    """
    queryset = LeaveRequest.objects.filter(
        employee=employee,
        status__in=[LeaveRequest.Status.PENDING, LeaveRequest.Status.APPROVED],
        start_date__lte=end_date,
        end_date__gte=start_date,
    )

    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)

    return queryset


@transaction.atomic
def apply_leave(*, employee, leave_type, start_date, end_date, reason="", created_by=None):
    """
    Submit a leave request and place a hold on the balance.

    Atomic because it writes two models. If the balance update failed after
    the request was created, you would have a request holding no days.
    """
    if not leave_type.is_active:
        raise ValidationError(f"{leave_type.name} is not currently available.")

    if end_date < start_date:
        raise ValidationError({"end_date": "End date cannot be before the start date."})

    if start_date < timezone.localdate():
        raise ValidationError({"start_date": "Leave cannot be applied for in the past."})

    days = working_days(start_date, end_date)
    if days == 0:
        raise ValidationError("That date range contains no working days.")

    clash = _overlapping_requests(employee, start_date, end_date).first()
    if clash:
        raise ValidationError(
            f"Overlaps an existing request ({clash.start_date} to {clash.end_date})."
        )

    # lock=True: nothing else may touch this balance until we commit.
    balance = get_balance(employee, leave_type, start_date.year, lock=True)

    if days > balance.available:
        raise ValidationError(
            f"Only {balance.available} day(s) of {leave_type.code} available, "
            f"but {days} requested."
        )

    leave_request = LeaveRequest.objects.create(
        employee=employee,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        days=days,
        reason=reason,
        created_by=created_by,
    )

    # The hold. Released by reject_leave or cancel_leave; converted to `used`
    # by approve_leave. Every path out of PENDING must deal with it.
    balance.pending += days
    balance.save(update_fields=["pending", "updated_at"])
    log_action(
        action=AuditLog.Action.CREATE,
        instance=leave_request,
        actor=created_by,
        changes={
            "leave_type": {"before": None, "after": leave_type.code},
            "dates": {"before": None, "after": f"{start_date} to {end_date}"},
            "days": {"before": None, "after": str(days)},
        },
    )

    return leave_request

 

def can_approve(user, leave_request):
    """
    Who may decide this request.

    - HR and Admin decide anything
    - A manager decides their own direct reports
    - Nobody decides their own request, manager or not

    This lives in the service, not a permission class, so the rule holds for
    the API, the admin, and the AI agent on Day 13. A permission class would
    only protect the HTTP path.
    """
    # Checked FIRST, so it also blocks a manager approving themselves.
    if leave_request.employee.user_id == user.id:
        return False

    Roles = user.Roles
    if user.role in (Roles.ADMIN, Roles.HR):
        return True

    manager = leave_request.employee.manager
    return manager is not None and manager.user_id == user.id


@transaction.atomic
def approve_leave(*, leave_request, approver, note=""):
    """
    Approve a request and convert its hold into used days.
    """
    if leave_request.status != LeaveRequest.Status.PENDING:
        raise ValidationError(
            f"This request is already {leave_request.get_status_display().lower()}."
        )

    before = snapshot(leave_request, ["status", "approver", "decided_at"])

    if not can_approve(approver, leave_request):
        raise PermissionDenied("You are not allowed to decide this request.")

    balance = get_balance(
        leave_request.employee,
        leave_request.leave_type,
        leave_request.start_date.year,
        lock=True,
    )

    # Both sides, always. Decrement pending WITHOUT incrementing used and the
    # employee silently gets their days back.
    balance.pending -= leave_request.days
    balance.used += leave_request.days
    balance.save(update_fields=["pending", "used", "updated_at"])

    leave_request.status = LeaveRequest.Status.APPROVED
    leave_request.approver = approver
    leave_request.decided_at = timezone.now()
    leave_request.decision_note = note
    leave_request.updated_by = approver
    leave_request.save(
        update_fields=[
            "status", "approver", "decided_at",
            "decision_note", "updated_by", "updated_at",
        ]
    )

    log_action(
        action=AuditLog.Action.APPROVE,
        instance=leave_request,
        actor=approver,
        changes=diff(before, snapshot(leave_request, ["status", "approver", "decided_at"])),
    )

    return leave_request

    


@transaction.atomic
def reject_leave(*, leave_request, approver, note=""):
    """
    Reject a request and release its hold.

    The days go back to available. Forgetting this is the classic bug in
    leave systems: rejected requests quietly eat someone's allowance and
    nobody notices until year end.
    """
    if leave_request.status != LeaveRequest.Status.PENDING:
        raise ValidationError(
            f"This request is already {leave_request.get_status_display().lower()}."
        )

    before = snapshot(leave_request, ["status", "approver", "decided_at"])

    if not can_approve(approver, leave_request):
        raise PermissionDenied("You are not allowed to decide this request.")

    balance = get_balance(
        leave_request.employee,
        leave_request.leave_type,
        leave_request.start_date.year,
        lock=True,
    )
    balance.pending -= leave_request.days
    balance.save(update_fields=["pending", "updated_at"])

    leave_request.status = LeaveRequest.Status.REJECTED
    leave_request.approver = approver
    leave_request.decided_at = timezone.now()
    leave_request.decision_note = note
    leave_request.updated_by = approver
    leave_request.save(
        update_fields=[
            "status", "approver", "decided_at",
            "decision_note", "updated_by", "updated_at",
        ]
    )

    log_action(
            action=AuditLog.Action.REJECT,
            instance=leave_request,
            actor=approver,
            changes=diff(before, snapshot(leave_request, ["status", "approver", "decided_at"])),
        )
    return leave_request


@transaction.atomic
def cancel_leave(*, leave_request, actor):
    """
    Withdraw a request.

    The employee may cancel their own; HR and Admin may cancel anyone's.
    A manager may not cancel their team's requests — rejecting is their tool.

    Only before the leave starts. You cannot un-take days already taken.
    """
    Roles = actor.Roles
    is_owner = leave_request.employee.user_id == actor.id

    if not (is_owner or actor.role in (Roles.ADMIN, Roles.HR)):
        raise PermissionDenied("You are not allowed to cancel this request.")

    if leave_request.status not in (
        LeaveRequest.Status.PENDING,
        LeaveRequest.Status.APPROVED,
    ):
        raise ValidationError(
            f"This request is already {leave_request.get_status_display().lower()}."
        )

    if leave_request.start_date <= timezone.localdate():
        raise ValidationError("Leave that has already started cannot be cancelled.")

    balance = get_balance(
        leave_request.employee,
        leave_request.leave_type,
        leave_request.start_date.year,
        lock=True,
    )

    # Which column holds the days depends on how far the request got.
    if leave_request.status == LeaveRequest.Status.PENDING:
        balance.pending -= leave_request.days
    else:
        balance.used -= leave_request.days
    balance.save(update_fields=["pending", "used", "updated_at"])

    leave_request.status = LeaveRequest.Status.CANCELLED
    leave_request.updated_by = actor
    leave_request.save(update_fields=["status", "updated_by", "updated_at"])

    return leave_request
