from django.contrib import admin

from .models import LeaveBalance, LeaveRequest, LeaveType


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "default_days_per_year", "is_paid", "is_active")
    list_filter = ("is_paid", "is_active")
    search_fields = ("name", "code")


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "year", "allocated", "used", "pending", "available")
    list_filter = ("year", "leave_type")
    search_fields = ("employee__employee_id", "employee__user__email")
    autocomplete_fields = ("employee", "leave_type")

    # HR sets the allocation. used and pending are owned by the service —
    # editing them here would silently desync them from LeaveRequest rows.
    readonly_fields = ("used", "pending")

    @admin.display(description="Available")
    def available(self, obj):
        return obj.available


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "start_date", "end_date", "days", "status")
    list_filter = ("status", "leave_type", "start_date")
    search_fields = ("employee__employee_id", "employee__user__email")
    autocomplete_fields = ("employee", "leave_type")

    # Everything a decision touches is read-only here. Flipping status in the
    # admin would approve leave WITHOUT moving pending -> used, leaving the
    # balance permanently wrong. Approvals go through leave/services.py only.
    readonly_fields = ("days", "status", "approver", "decided_at")
