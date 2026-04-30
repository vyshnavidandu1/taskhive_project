from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Project, ProjectMembership, ProjectActivity
from .forms import ProjectForm
from tasks.models import Task


@login_required
def project_list_view(request):
    user = request.user
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    sort = request.GET.get('sort', '-created_at')

    if user.is_admin:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members=user)
        ).distinct()

    if query:
        projects = projects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if status:
        projects = projects.filter(status=status)

    valid_sorts = ['name', '-name', '-created_at', 'created_at', 'end_date', '-end_date']
    if sort in valid_sorts:
        projects = projects.order_by(sort)

    projects = projects.annotate(task_count=Count('tasks'))

    context = {
        'projects': projects,
        'query': query,
        'selected_status': status,
        'sort': sort,
        'status_choices': Project.STATUS_CHOICES,
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.user_can_access(request.user):
        messages.error(request, 'You do not have access to this project.')
        return redirect('project_list')

    tasks = project.tasks.all()
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    task_stats = {
        'total': project.tasks.count(),
        'todo': project.tasks.filter(status='todo').count(),
        'in_progress': project.tasks.filter(status='in_progress').count(),
        'completed': project.tasks.filter(status='completed').count(),
    }

    members = project.get_all_members()
    activities = project.activities.select_related('user')[:15]

    context = {
        'project': project,
        'tasks': tasks,
        'task_stats': task_stats,
        'members': members,
        'activities': activities,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'task_status_choices': Task.STATUS_CHOICES,
        'task_priority_choices': Task.PRIORITY_CHOICES,
        'can_manage': project.user_can_manage(request.user),
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_create_view(request):
    if not request.user.is_manager:
        messages.error(request, 'Only managers and admins can create projects.')
        return redirect('project_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_members(project)
            ProjectActivity.objects.create(
                project=project, user=request.user,
                action=f'Project "{project.name}" was created.'
            )
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(user=request.user)

    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Create'})


@login_required
def project_edit_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.user_can_manage(request.user):
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project, user=request.user)
        if form.is_valid():
            form.save()
            form.save_members(project)
            ProjectActivity.objects.create(
                project=project, user=request.user,
                action=f'Project settings updated.'
            )
            messages.success(request, 'Project updated successfully.')
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project, user=request.user)

    return render(request, 'projects/project_form.html', {'form': form, 'project': project, 'action': 'Edit'})


@login_required
def project_delete_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.user_can_manage(request.user):
        messages.error(request, 'You do not have permission to delete this project.')
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        name = project.name
        project.delete()
        messages.success(request, f'Project "{name}" deleted.')
        return redirect('project_list')

    return render(request, 'projects/project_confirm_delete.html', {'project': project})
