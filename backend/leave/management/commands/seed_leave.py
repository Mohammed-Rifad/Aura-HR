from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from employees.models import Employee
from leave.models import LeaveBalance, LeaveType


class Command(BaseCommand):
    help = "Create leave types and allocate this year's balances (dev only)"

    TYPES = [
        {"name": "Annual Leave", "code": "ANNUAL", "default_days_per_year": 30, "is_paid": True},
        {"name": "Sick Leave", "code": "SICK", "default_days_per_year": 15, "is_paid": True},
        {"name": "Maternity Leave", "code": "MATERNITY", "default_days_per_year": 60, "is_paid": True},
        {"name": "Unpaid Leave", "code": "UNPAID", "default_days_per_year": 0, "is_paid": False},
    ]

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_leave is development-only.")

        year = date.today().year

        types = []
        for data in self.TYPES:
            leave_type, created = LeaveType.objects.get_or_create(
                code=data["code"], defaults=data
            )
            types.append(leave_type)
            self.stdout.write(
                self.style.SUCCESS(f"Created type: {leave_type.name}")
                if created
                else self.style.WARNING(f"Exists: {leave_type.name}")
            )

        created_count = 0
        for employee in Employee.objects.all():
            for leave_type in types:
                _, created = LeaveBalance.objects.get_or_create(
                    employee=employee,
                    leave_type=leave_type,
                    year=year,
                    defaults={"allocated": leave_type.default_days_per_year},
                )
                created_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n{created_count} balances created for {year}."
            )
        )
