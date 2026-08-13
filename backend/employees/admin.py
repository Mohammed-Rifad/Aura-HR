from django.contrib import admin

from .models import Employee, EmployeeDocument
from .services import generate_employee_id


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user", "department", "designation", "status")
    list_filter = ("status", "employment_type", "department")
    search_fields = ("employee_id", "user__email", "user__first_name", "user__last_name")
    autocomplete_fields = ("department", "designation", "manager")
    inlines = [EmployeeDocumentInline]
    readonly_fields = ("employee_id",)

    def save_model(self, request, obj, form, change):
        # The model no longer generates the ID, so the admin has to ask the
        # service for one. Leaving it blank would break the unique
        # constraint the moment a second employee was added.
        if not obj.employee_id:
            obj.employee_id = generate_employee_id(obj.department)
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ("employee", "document_type", "document_number", "expiry_date")
    list_filter = ("document_type",)
    search_fields = ("employee__employee_id", "document_number")
