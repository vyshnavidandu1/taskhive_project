from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('user', 'task', 'message_preview', 'created_at', 'is_edited')
    list_filter = ('created_at', 'is_edited')
    search_fields = ('user__username', 'task__title', 'message')
    readonly_fields = ('created_at', 'updated_at')

    def message_preview(self, obj):
        return obj.message[:60] + '...' if len(obj.message) > 60 else obj.message
    message_preview.short_description = 'Message'
