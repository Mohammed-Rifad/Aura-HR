import uuid

from django.db import models

from common.models import BaseModel
from employees.models import Employee


class Attendance(BaseModel):
    """One row per employee, per day."""

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        HALF_DAY = "HALF_DAY", "Half Day"
        ABSENT = "ABSENT", "Absent"
        ON_LEAVE = "ON_LEAVE", "On Leave"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="attendance"
    )

    # The working day this row belongs to. For an overnight shift this is
    # the check-IN date, never the check-out date.
    date = models.DateField(db_index=True)

    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    # Filled in on check-out. Stored, not calculated on the fly, so changing
    # the rules later cannot rewrite what someone worked last year.
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
        db_index=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                name="unique_attendance_per_day",
            )
        ]
        indexes = [
            models.Index(fields=["employee", "-date"]),
        ]

    def __str__(self):
        return f"{self.employee.employee_id} {self.date}"
