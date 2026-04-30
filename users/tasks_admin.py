from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Task


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ('title', 'project', 'assigned_user', 'priority', 'status', 'deadline', 'is_overdue')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'project__name', 'assigned_user__username')
    list_editable = ('status', 'priority')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('assigned_user', 'created_by')

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'
