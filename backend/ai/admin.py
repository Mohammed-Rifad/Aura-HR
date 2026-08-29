from django.contrib import admin

from .models import AIToolCall, Conversation, Message


@admin.register(AIToolCall)
class AIToolCallAdmin(admin.ModelAdmin):
    list_display = (
        "created_at", "tool_name", "actor_label", "allowed", "duration_ms"
    )
    list_filter = ("tool_name", "allowed", "created_at")
    search_fields = ("actor_label", "tool_name", "error")
    date_hierarchy = "created_at"

    # Evidence. Nobody edits it, including staff.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
