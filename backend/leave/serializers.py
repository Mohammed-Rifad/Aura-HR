from rest_framework import serializers

from employees.serializers import EmployeeListSerializer
from users.serializers import UserSerializer

from .models import LeaveBalance, LeaveRequest, LeaveType
from .services import apply_leave


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id", "name", "code", "default_days_per_year", "is_paid"]


class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer(read_only=True)
    # `available` is a property on the model, not a column. DRF reads it the
    # same way it reads a field.
    available = serializers.DecimalField(
        max_digits=5, decimal_places=1, read_only=True
    )

    class Meta:
        model = LeaveBalance
        fields = [
            "id", "leave_type", "year",
            "allocated", "used", "pending", "available",
        ]


class LeaveRequestListSerializer(serializers.ModelSerializer):
    """Small payload for the requests table and the approvals inbox."""

    employee_code = serializers.CharField(source="employee.employee_id", read_only=True)
    employee_name = serializers.CharField(
        source="employee.user.get_full_name", read_only=True
    )
    leave_type_code = serializers.CharField(source="leave_type.code", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id", "employee_code", "employee_name", "leave_type_code",
            "start_date", "end_date", "days", "status", "status_display",
        ]


class LeaveRequestDetailSerializer(serializers.ModelSerializer):
    employee = EmployeeListSerializer(read_only=True)
    leave_type = LeaveTypeSerializer(read_only=True)
    approver = UserSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id", "employee", "leave_type",
            "start_date", "end_date", "days", "reason",
            "status", "status_display",
            "approver", "decided_at", "decision_note",
            "created_at", "updated_at",
        ]


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    """
    The four things a person actually chooses.

    days, status, employee and approver are all decided by the service —
    exposing any of them would let a client set them directly.
    """

    # Inactive types can't be applied for. Same pattern as the `user` field
    # on EmployeeWriteSerializer: a narrow queryset IS the validation.
    leave_type = serializers.PrimaryKeyRelatedField(
        queryset=LeaveType.objects.filter(is_active=True)
    )

    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]

    def create(self, validated_data):
        user = self.context["request"].user
        employee = getattr(user, "employee", None)

        if employee is None:
            raise serializers.ValidationError(
                "Your account has no employee record, so you cannot apply for leave."
            )

        return apply_leave(employee=employee, created_by=user, **validated_data)


class LeaveDecisionSerializer(serializers.Serializer):
    """Body for the approve and reject actions. Just an optional note."""

    note = serializers.CharField(required=False, allow_blank=True, default="")
