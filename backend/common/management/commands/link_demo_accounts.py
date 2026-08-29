"""
Wire the four well-known login accounts into the org chart.

seed_demo creates 66 people with generated emails. Nobody can demo a
manager's view by logging in as `christopher.hall@aurahr.com`, so this
attaches admin/hr/manager/employee@aurahr.com to real positions:

    manager@aurahr.com    Director of Engineering, with a real team
    employee@aurahr.com   Engineer reporting to that manager
    hr@aurahr.com         HR Director, so leave balances exist
    admin@aurahr.com      Operations Director

Idempotent — safe to run more than once.

    python manage.py link_demo_accounts
"""

from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from employees.models import Employee
from employees.services import create_employee
from leave.models import LeaveBalance, LeaveType
from organizations.models import Department, Designation

User = get_user_model()

# email -> (department code, designation title, reports to this email)
POSITIONS = [
    ("manager@aurahr.com", "ENG", "Director", None),
    ("hr@aurahr.com", "HRD", "Director", None),
    ("admin@aurahr.com", "OPS", "Director", None),
    ("employee@aurahr.com", "ENG", "Engineer", "manager@aurahr.com"),
]

TEAM_SIZE = 8


class Command(BaseCommand):
    help = "Give the demo login accounts real positions in the org chart"

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("link_demo_accounts is development-only.")

        employees = {}

        for email, dept_code, title, manager_email in POSITIONS:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"skip {email} — no such user")
                )
                continue

            existing = Employee.objects.filter(user=user).first()
            if existing:
                employees[email] = existing
                self.stdout.write(f"exists  {email}  {existing.employee_id}")
                continue

            department = Department.objects.filter(code=dept_code).first()
            designation = Designation.objects.filter(title=title).first()
            if department is None or designation is None:
                raise CommandError(
                    f"Missing {dept_code}/{title}. Run `manage.py seed_demo` first."
                )

            employee = create_employee(
                user=user,
                department=department,
                designation=designation,
                manager=employees.get(manager_email),
                date_of_joining=date.today() - timedelta(days=900),
                created_by=user,
            )
            employees[email] = employee
            self.stdout.write(
                self.style.SUCCESS(f"created {email}  {employee.employee_id}")
            )

        self._build_team(employees.get("manager@aurahr.com"))
        self._balances(employees.values())

        self.stdout.write(self.style.SUCCESS("\nDemo accounts linked."))

    def _build_team(self, manager):
        """
        Move some existing Engineering people under the demo manager.

        Without a team, logging in as manager@aurahr.com shows the same empty
        screen as an ordinary employee — which defeats the point of having a
        manager account to demo with.
        """
        if manager is None:
            return

        candidates = (
            Employee.objects.filter(department=manager.department)
            .exclude(pk=manager.pk)
            .exclude(manager=manager)
            .order_by("employee_id")[:TEAM_SIZE]
        )

        moved = Employee.objects.filter(
            pk__in=[employee.pk for employee in candidates]
        ).update(manager=manager)

        self.stdout.write(f"team     {moved} people now report to the demo manager")

    def _balances(self, employees):
        """Leave balances, so the demo accounts can actually apply for leave."""
        year = timezone.localdate().year
        rows = [
            LeaveBalance(
                employee=employee,
                leave_type=leave_type,
                year=year,
                allocated=leave_type.default_days_per_year,
            )
            for employee in employees
            for leave_type in LeaveType.objects.filter(is_active=True)
        ]
        LeaveBalance.objects.bulk_create(rows, ignore_conflicts=True)
        self.stdout.write(f"balances {len(rows)} ensured")
