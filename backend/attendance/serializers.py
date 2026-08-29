from rest_framework import serializers

from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField(
        source="employee.employee_id", read_only=True
    )
    employee_name = serializers.CharField(
        source="employee.user.get_full_name", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            "id", "employee_code", "employee_name", "date",
            "check_in", "check_out", "work_hours",
            "status", "status_display", "notes",
        ]
        # Everything. The service writes attendance; the API only reads it.
        read_only_fields = fields


class MonthlySummarySerializer(serializers.Serializer):
    """Output shape for the summary action. Not backed by a model."""

    year = serializers.IntegerField()
    month = serializers.IntegerField()
    days_recorded = serializers.IntegerField()
    total_hours = serializers.DecimalField(max_digits=7, decimal_places=2)
    present = serializers.IntegerField()
    half_day = serializers.IntegerField()
    absent = serializers.IntegerField()
    on_leave = serializers.IntegerField()
