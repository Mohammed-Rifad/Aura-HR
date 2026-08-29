from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at", "actor_label", "action", "model_name", "object_label"
    )
    list_filter = ("action", "model_name", "created_at")
    search_fields = ("actor_label", "object_id", "object_label")
    date_hierarchy = "created_at"

    # Append-only, enforced. Not even a superuser edits evidence.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
