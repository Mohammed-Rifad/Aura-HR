"""
Business logic for employees.

Everything that creates an employee goes through here — the API, the admin,
the seed command, and later the bulk importer. Keeping it in one place is
what makes the employee_id rules enforceable.
"""

import random

from django.db import transaction

from .models import Employee

ID_ATTEMPTS = 10
ID_RANGE = (1000, 9999)


def generate_employee_id(department):
    """
    Build a code like FIN4821 from the department code plus random digits.

    Random rather than sequential so the code doesn't advertise headcount.
    Collisions are possible, so we check and retry.

    Note: `all_objects`, not `objects`. A soft-deleted employee still holds
    their row in the database, and therefore still holds their code.
    """
    prefix = (department.code or "").strip().upper()
    if not prefix:
        raise ValueError(f"Department {department.pk} has no code set.")

    for _ in range(ID_ATTEMPTS):
        candidate = f"{prefix}{random.randint(*ID_RANGE)}"
        if not Employee.all_objects.filter(employee_id=candidate).exists():
            return candidate

    raise ValueError(
        f"Could not generate a unique employee ID for '{prefix}' "
        f"after {ID_ATTEMPTS} attempts."
    )


@transaction.atomic
def create_employee(*, employee_id=None, created_by=None, **fields):
    """
    Create an employee, generating the ID unless one was supplied.

    A supplied `employee_id` always wins. That is what makes importing from
    a previous HR system possible — those people already have codes and
    changing them would break their history.

    Keyword-only arguments on purpose: create_employee(user, dept, desig)
    is easy to get in the wrong order, create_employee(user=..., ...) isn't.
    """
    department = fields.get("department")
    if department is None:
        raise ValueError("department is required to create an employee.")

    return Employee.objects.create(
        employee_id=employee_id or generate_employee_id(department),
        created_by=created_by,
        **fields,
    )
