from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from .models import Project, ProjectActivity
from tasks.models import Task


@login_required
def dashboard_view(request):
    user = request.user

    if user.is_admin:
        projects = Project.objects.all()
        tasks = Task.objects.all()
    else:
        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members=user)
        ).distinct()
        tasks = Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(assigned_user=user)
        ).distinct()

    today = timezone.now().date()

    # Project stats
    total_projects = projects.count()
    active_projects = projects.filter(status='active').count()
    completed_projects = projects.filter(status='completed').count()

    # Task stats
    total_tasks = tasks.count()
    todo_tasks = tasks.filter(status='todo').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    completed_tasks = tasks.filter(status='completed').count()

    # Upcoming deadlines (next 7 days)
    upcoming_tasks = tasks.filter(
        deadline__gte=today,
        deadline__lte=today + timezone.timedelta(days=7),
        status__in=['todo', 'in_progress']
    ).order_by('deadline').select_related('project', 'assigned_user')[:8]

    # Overdue tasks
    overdue_tasks = tasks.filter(
        deadline__lt=today,
        status__in=['todo', 'in_progress']
    ).count()

    # My tasks
    my_tasks = Task.objects.filter(
        assigned_user=user,
        status__in=['todo', 'in_progress']
    ).order_by('deadline')[:6]

    # Recent activity
    if user.is_admin:
        activities = ProjectActivity.objects.select_related('project', 'user').order_by('-created_at')[:10]
    else:
        project_ids = projects.values_list('id', flat=True)
        activities = ProjectActivity.objects.filter(
            project_id__in=project_ids
        ).select_related('project', 'user').order_by('-created_at')[:10]

    # Recent projects
    recent_projects = projects.order_by('-updated_at')[:5]

    # Priority breakdown
    high_priority = tasks.filter(priority='high', status__in=['todo', 'in_progress']).count()
    medium_priority = tasks.filter(priority='medium', status__in=['todo', 'in_progress']).count()
    low_priority = tasks.filter(priority='low', status__in=['todo', 'in_progress']).count()

    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_tasks': total_tasks,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'upcoming_tasks': upcoming_tasks,
        'my_tasks': my_tasks,
        'activities': activities,
        'recent_projects': recent_projects,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'today': today,
    }
    return render(request, 'dashboard.html', context)
