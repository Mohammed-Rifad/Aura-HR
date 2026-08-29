"""
The whole approval gate, end to end.

  1. A manager asks the AI to approve leave  → nothing happens yet
  2. The manager clicks Approve              → it happens
  3. The manager clicks Approve again        → blocked
  4. A normal employee tries the same thing  → blocked

Run with:  python test_approval.py
"""

import os

import django
from datetime import timedelta
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone

from employees.models import Employee
from leave.models import LeaveRequest, LeaveType
from leave.services import apply_leave, get_balance
from ai.models import Conversation
from ai.services import ask, decide
from leave.models import LeaveRequest
from leave.services import get_balance
from users.models import User





manager = User.objects.get(email="manager@aurahr.com")

target = (
    LeaveRequest.objects.filter(status="PENDING", employee__manager__user=manager)
    .select_related("employee__user", "leave_type")
    .first()
)
if target is None:
    # Earlier runs approved everything there was. Create a fresh request so
    # this script can be run over and over.
    employee = Employee.objects.filter(manager__user=manager).first()
    leave_type = LeaveType.objects.get(code="ANNUAL")

    # A month out, starting on a weekday — apply_leave rejects past dates
    # and ranges containing no working days.
    start = timezone.localdate() + timedelta(days=30)
    while start.weekday() >= 5:
        start += timedelta(days=1)

    target = apply_leave(
        employee=employee,
        leave_type=leave_type,
        start_date=start,
        end_date=start + timedelta(days=2),
        reason="Seeded by test_approval.py",
    )
    print("No pending request found — created one for the test.")

target = (
    LeaveRequest.objects.select_related("employee__user", "leave_type")
    .get(pk=target.pk)
)
name = target.employee.user.get_full_name()

 
print(f"Target: {name} — {target.days} days {target.leave_type.name}, "
      f"{target.start_date} to {target.end_date}")

before = get_balance(target.employee, target.leave_type, target.start_date.year)
print(f"Balance before: used={before.used} pending={before.pending} "
      f"available={before.available}")


print("\n" + "=" * 70)
print("STEP 1 — the manager asks")
print("=" * 70)

conversation = Conversation.objects.create(user=manager)
print("AI:", ask(
    conversation=conversation,
    question=f"Approve the pending leave request for {name}.",
    user=manager,
))

action = conversation.pending_actions.order_by("-created_at").first()
target.refresh_from_db()

print("\nProposed :", action.summary if action else "NOTHING — the model did not propose")
print("Leave is :", target.status, "  <-- must still be PENDING")


print("\n" + "=" * 70)
print("STEP 2 — the manager clicks Approve")
print("=" * 70)

action, answer = decide(action_id=action.id, user=manager, approve=True)
print("AI:", answer)

target.refresh_from_db()
after = get_balance(target.employee, target.leave_type, target.start_date.year)
print("\nLeave is :", target.status, "  <-- must be APPROVED")
print(f"Balance after : used={after.used} pending={after.pending} "
      f"available={after.available}")


print("\n" + "=" * 70)
print("STEP 3 — the manager clicks Approve again")
print("=" * 70)

try:
    decide(action_id=action.id, user=manager, approve=True)
    print("*** BUG: it ran a second time ***")
except Exception as exc:
    print("Blocked:", exc)


print("\n" + "=" * 70)
print("STEP 4 — a normal employee tries the same thing")
print("=" * 70)

aaron = User.objects.get(email="aaron.nguyen@aurahr.com")
aaron_chat = Conversation.objects.create(user=aaron)
print("AI:", ask(
    conversation=aaron_chat,
    question=f"Approve the pending leave request for {name}.",
    user=aaron,
))
print("Proposed:", aaron_chat.pending_actions.count(), " <-- must be 0")
