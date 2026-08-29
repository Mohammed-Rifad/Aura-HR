"""
Create one pending leave request so the approval card has something to show.

Run with:  python seed_pending.py
"""

import os
from datetime import timedelta

import django
from django.core.exceptions import ValidationError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone

from employees.models import Employee
from leave.models import LeaveType
from leave.services import apply_leave
from users.models import User

manager = User.objects.get(email="manager@aurahr.com")
employee = Employee.objects.filter(manager__user=manager).select_related("user").first()
leave_type = LeaveType.objects.get(code="ANNUAL")

# A month out, starting on a weekday — apply_leave rejects past dates and
# ranges with no working days in them.
start = timezone.localdate() + timedelta(days=45)
while start.weekday() >= 5:
    start += timedelta(days=1)

# Walk forward until a free window turns up. Earlier runs of this script
# already took the obvious dates, and apply_leave rejects overlaps.
request = None
start = timezone.localdate() + timedelta(days=45)

for _ in range(12):
    while start.weekday() >= 5:
        start += timedelta(days=1)
    try:
        request = apply_leave(
            employee=employee,
            leave_type=leave_type,
            start_date=start,
            end_date=start + timedelta(days=2),
            reason="Family event",
        )
        break
    except ValidationError:
        start += timedelta(days=14)

if request is None:
    raise SystemExit("No free window in the next six months — approve or cancel some.")

print(
    f"Created request {request.id}: {employee.user.get_full_name()}, "
    f"{request.days} days {leave_type.name}, {request.start_date} to {request.end_date}"
)
