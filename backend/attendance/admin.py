from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "check_in", "check_out", "work_hours", "status")
    list_filter = ("status", "date")
    search_fields = ("employee__employee_id", "employee__user__email")
    autocomplete_fields = ("employee",)
    date_hierarchy = "date"

    # Written by the service, from the clock. Editing hours by hand here
    # would be untraceable.
    readonly_fields = ("check_in", "check_out", "work_hours")
