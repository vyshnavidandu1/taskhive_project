from django import template

register = template.Library()


@register.filter(name='can_manage')
def can_manage(project, user):
    """Check if user can manage a project: {{ project|can_manage:request.user }}"""
    return project.user_can_manage(user)


@register.filter(name='can_access')
def can_access(project, user):
    """Check if user can access a project."""
    return project.user_can_access(user)


@register.simple_tag
def task_status_label(status):
    labels = {
        'todo': 'To Do',
        'in_progress': 'In Progress',
        'review': 'In Review',
        'completed': 'Completed',
    }
    return labels.get(status, status)


@register.filter(name='priority_color')
def priority_color(priority):
    colors = {
        'low': 'success',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'dark',
    }
    return colors.get(priority, 'secondary')
