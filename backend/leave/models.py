from django.conf import settings
from django.db import models

from common.models import BaseModel
from employees.models import Employee


class LeaveType(BaseModel):
    """Annual, Sick, Unpaid. Configured by HR, not hardcoded."""

    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    default_days_per_year = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LeaveBalance(BaseModel):
    """
    One row per employee, per leave type, per year.

    Three numbers, not two. `pending` holds days that are applied for but
    not yet decided — without it, someone with 10 days left can submit two
    separate 8-day requests and both pass validation.
    """

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leave_balances"
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.PROTECT, related_name="balances"
    )
    year = models.PositiveIntegerField()

    allocated = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    pending = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        ordering = ["-year", "leave_type__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "leave_type", "year"],
                name="unique_balance_per_year",
            )
        ]

    @property
    def available(self):
        return self.allocated - self.used - self.pending

    def __str__(self):
        return f"{self.employee.employee_id} {self.leave_type.code} {self.year}"


class LeaveRequest(BaseModel):
    """An application for leave, and its decision."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="leave_requests"
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.PROTECT, related_name="requests"
    )

    start_date = models.DateField()
    end_date = models.DateField()
    # Calculated by the service, not sent by the client. Stored because the
    # working-day rules could change and history must stay accurate.
    days = models.DecimalField(max_digits=5, decimal_places=1)

    reason = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_decisions",
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]
        indexes = [
            # The overlap check filters by employee and status, then ranges
            # over dates. Equality columns first, range columns last.
            models.Index(fields=["employee", "status", "start_date"]),
        ]

    def __str__(self):
        return f"{self.employee.employee_id} {self.leave_type.code} {self.start_date}"
