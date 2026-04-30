from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Project, ProjectMembership, ProjectActivity


class ProjectMembershipInline(TabularInline):
    model = ProjectMembership
    extra = 1


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ('name', 'owner', 'status', 'start_date', 'end_date', 'created_at', 'progress_percentage')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    inlines = [ProjectMembershipInline]
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def progress_percentage(self, obj):
        return f"{obj.progress_percentage}%"
    progress_percentage.short_description = 'Progress'


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(ModelAdmin):
    list_display = ('project', 'user', 'role', 'joined_at')
    list_filter = ('role',)
    search_fields = ('project__name', 'user__username')


@admin.register(ProjectActivity)
class ProjectActivityAdmin(ModelAdmin):
    list_display = ('project', 'user', 'action', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('project__name', 'action')
    readonly_fields = ('created_at',)
