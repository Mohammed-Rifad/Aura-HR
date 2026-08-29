"""
Generate a realistic demo dataset.

Development only. Run after seed_users and seed_leave:

    python manage.py seed_demo
    python manage.py seed_demo --employees 40

Departments, designations and leave balances are created with get_or_create,
so re-running is safe. Employees, leave requests and attendance are additive —
re-running adds more history rather than replacing it.
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from faker import Faker

from attendance.models import Attendance
from employees.models import Employee, EmployeeDocument
from employees.services import create_employee
from leave.models import LeaveBalance, LeaveRequest, LeaveType
from leave.services import apply_leave, approve_leave, reject_leave
from organizations.models import Department, Designation

User = get_user_model()

DEPARTMENTS = [
    ("Engineering", "ENG"),
    ("Finance", "FIN"),
    ("Human Resources", "HRD"),
    ("Sales", "SLS"),
    ("Operations", "OPS"),
    ("Marketing", "MKT"),
]

# Rough seniority order — index 0 is the most senior, used to pick heads.
DESIGNATIONS = [
    "Director",
    "Senior Manager",
    "Manager",
    "Team Lead",
    "Senior Engineer",
    "Engineer",
    "Analyst",
    "Executive",
    "Associate",
    "Intern",
]

DOCUMENT_TYPES = [
    EmployeeDocument.DocumentType.PASSPORT,
    EmployeeDocument.DocumentType.VISA,
    EmployeeDocument.DocumentType.EMIRATES_ID,
    EmployeeDocument.DocumentType.CONTRACT,
]

# How far in the future each document expires. The 10-30 day bucket is what
# the Day 14 compliance demo asks about, so it is deliberately well populated.
EXPIRY_BUCKETS = [
    (10, 30, 0.25),
    (31, 60, 0.20),
    (-180, -5, 0.10),   # already expired
    (200, 900, 0.45),
]

DEMO_PASSWORD = "Password@123"
ATTENDANCE_DAYS = 60


class Command(BaseCommand):
    help = "Create a realistic demo dataset (development only)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--employees",
            type=int,
            default=70,
            help="How many employees to create (default 70)",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Random seed, so re-runs produce the same people",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo is development-only.")

        # Fixed seed: the same command produces the same company every time,
        # which makes screenshots and demo scripts reproducible.
        random.seed(options["seed"])
        self.fake = Faker()
        Faker.seed(options["seed"])

        target = options["employees"]

        departments = self._departments()
        designations = self._designations()
        leave_types = self._leave_types()

        employees = self._employees(target, departments, designations)
        self._balances(employees, leave_types)
        self._leave_history(employees, leave_types)
        self._attendance(employees)
        self._documents(employees)

        self.stdout.write(self.style.SUCCESS("\nDemo data ready."))
        self.stdout.write(
            f"  employees   {Employee.objects.count()}\n"
            f"  balances    {LeaveBalance.objects.count()}\n"
            f"  leave       {LeaveRequest.objects.count()}\n"
            f"  attendance  {Attendance.objects.count()}\n"
            f"  documents   {EmployeeDocument.objects.count()}"
        )

    # -- reference data ----------------------------------------------------

    def _departments(self):
        result = []
        for name, code in DEPARTMENTS:
            department, _ = Department.objects.get_or_create(
                code=code, defaults={"name": name}
            )
            result.append(department)
        self.stdout.write(f"departments  {len(result)}")
        return result

    def _designations(self):
        result = []
        for title in DESIGNATIONS:
            designation, _ = Designation.objects.get_or_create(title=title)
            result.append(designation)
        self.stdout.write(f"designations {len(result)}")
        return result

    def _leave_types(self):
        types = list(LeaveType.objects.filter(is_active=True))
        if not types:
            raise CommandError("No leave types. Run `manage.py seed_leave` first.")
        return types

    # -- people ------------------------------------------------------------

    def _unique_email(self, first, last):
        base = f"{first}.{last}".lower().replace(" ", "").replace("'", "")
        email = f"{base}@aurahr.com"
        suffix = 1
        while User.objects.filter(email=email).exists():
            suffix += 1
            email = f"{base}{suffix}@aurahr.com"
        return email

    def _make_person(self, department, designation, manager, role):
        first = self.fake.first_name()
        last = self.fake.last_name()

        user = User.objects.create_user(
            email=self._unique_email(first, last),
            password=DEMO_PASSWORD,
            first_name=first,
            last_name=last,
            phone=f"+9715{random.randint(10000000, 99999999)}",
            role=role,
            is_verified=True,
            is_active=True,
        )

        joined = timezone.localdate() - timedelta(days=random.randint(60, 2000))

        return create_employee(
            user=user,
            department=department,
            designation=designation,
            manager=manager,
            date_of_joining=joined,
            date_of_birth=joined - timedelta(days=random.randint(7000, 15000)),
            employment_type=random.choices(
                [
                    Employee.EmploymentType.FULL_TIME,
                    Employee.EmploymentType.CONTRACT,
                    Employee.EmploymentType.INTERN,
                ],
                weights=[80, 15, 5],
            )[0],
        )

    def _employees(self, target, departments, designations):
        """
        Two levels: one head per department, everyone else reports to them.

        Deep hierarchies look impressive but make the manager-visibility demo
        harder to explain. Two levels is enough to show scoping working.
        """
        created = []
        per_department = max(2, target // len(departments))

        for department in departments:
            head = self._make_person(
                department=department,
                designation=designations[0],          # Director
                manager=None,
                role=User.Roles.MANAGER,
            )
            created.append(head)

            for _ in range(per_department - 1):
                created.append(
                    self._make_person(
                        department=department,
                        designation=random.choice(designations[3:]),
                        manager=head,
                        role=User.Roles.EMPLOYEE,
                    )
                )

        self.stdout.write(f"employees    {len(created)} created")
        return created

    # -- leave -------------------------------------------------------------

    def _balances(self, employees, leave_types):
        year = timezone.localdate().year
        rows = []
        for employee in employees:
            for leave_type in leave_types:
                rows.append(
                    LeaveBalance(
                        employee=employee,
                        leave_type=leave_type,
                        year=year,
                        allocated=Decimal(leave_type.default_days_per_year),
                    )
                )
        LeaveBalance.objects.bulk_create(rows, ignore_conflicts=True, batch_size=500)
        self.stdout.write(f"balances     {len(rows)}")

    def _leave_history(self, employees, leave_types):
        """
        A spread of statuses, all created through the service so the balance
        arithmetic and audit rows are real rather than fabricated.

        Only future dates: apply_leave refuses to book leave in the past, and
        working around that rule in a seed script would mean the seeded data
        no longer proves the rule works.
        """
        approver = User.objects.filter(role=User.Roles.HR).first()
        if approver is None:
            self.stdout.write(self.style.WARNING("No HR user — skipping leave."))
            return

        today = timezone.localdate()
        applied = approved = rejected = 0

        for employee in employees:
            for _ in range(random.randint(0, 3)):
                start = today + timedelta(days=random.randint(3, 120))
                end = start + timedelta(days=random.randint(0, 6))
                try:
                    request = apply_leave(
                        employee=employee,
                        leave_type=random.choice(leave_types),
                        start_date=start,
                        end_date=end,
                        reason=self.fake.sentence(nb_words=6),
                        created_by=employee.user,
                    )
                except ValidationError:
                    continue        # overlap or no balance left — fine, skip

                applied += 1

                roll = random.random()
                try:
                    if roll < 0.55:
                        approve_leave(leave_request=request, approver=approver)
                        approved += 1
                    elif roll < 0.70:
                        reject_leave(
                            leave_request=request,
                            approver=approver,
                            note="Team coverage.",
                        )
                        rejected += 1
                    # the rest stay PENDING, which fills the approvals inbox
                except (ValidationError, PermissionDenied):
                    continue

        self.stdout.write(
            f"leave        {applied} applied, {approved} approved, {rejected} rejected"
        )

    # -- attendance --------------------------------------------------------

    def _attendance(self, employees):
        """
        Weekday records for the last ATTENDANCE_DAYS days.

        bulk_create, not the check_in/check_out service. Three thousand rows
        through the service would mean three thousand audit entries for data
        that never actually happened.
        """
        today = timezone.localdate()
        rows = []

        for employee in employees:
            for offset in range(1, ATTENDANCE_DAYS + 1):
                day = today - timedelta(days=offset)
                if day.weekday() in (5, 6):
                    continue
                if day < employee.date_of_joining:
                    continue

                roll = random.random()
                if roll < 0.04:
                    status, hours = Attendance.Status.ABSENT, Decimal("0")
                elif roll < 0.10:
                    status, hours = Attendance.Status.HALF_DAY, Decimal("4.0")
                else:
                    status = Attendance.Status.PRESENT
                    hours = Decimal(str(round(random.uniform(7.5, 9.5), 2)))

                start_hour = random.randint(8, 10)
                check_in = timezone.make_aware(
                    timezone.datetime(day.year, day.month, day.day, start_hour,
                                      random.randint(0, 59))
                )

                rows.append(
                    Attendance(
                        employee=employee,
                        date=day,
                        check_in=None if status == Attendance.Status.ABSENT else check_in,
                        check_out=(
                            None
                            if status == Attendance.Status.ABSENT
                            else check_in + timedelta(hours=float(hours))
                        ),
                        work_hours=hours,
                        status=status,
                    )
                )

        Attendance.objects.bulk_create(rows, ignore_conflicts=True, batch_size=1000)
        self.stdout.write(f"attendance   {len(rows)}")

    # -- documents ---------------------------------------------------------

    def _pick_expiry(self, today):
        low, high, _ = random.choices(
            EXPIRY_BUCKETS, weights=[bucket[2] for bucket in EXPIRY_BUCKETS]
        )[0]
        return today + timedelta(days=random.randint(low, high))

    def _documents(self, employees):
        """
        Documents with staggered expiry dates.

        `file` holds a path only — no bytes are written. The compliance demo
        reads expiry_date, not file contents. Day 14's RAG work needs a few
        real uploads on top of this.
        """
        today = timezone.localdate()
        rows = []

        for employee in employees:
            for document_type in random.sample(DOCUMENT_TYPES, random.randint(1, 3)):
                expiry = self._pick_expiry(today)
                rows.append(
                    EmployeeDocument(
                        employee=employee,
                        document_type=document_type,
                        document_number=self.fake.bothify("??######").upper(),
                        file=f"employee_documents/demo/{employee.employee_id}_{document_type}.pdf",
                        issue_date=expiry - timedelta(days=random.choice([365, 730, 1825])),
                        expiry_date=expiry,
                    )
                )

        EmployeeDocument.objects.bulk_create(rows, batch_size=500)

        expiring = EmployeeDocument.objects.filter(
            expiry_date__gte=today, expiry_date__lte=today + timedelta(days=30)
        ).count()
        self.stdout.write(f"documents    {len(rows)} ({expiring} expiring within 30 days)")
