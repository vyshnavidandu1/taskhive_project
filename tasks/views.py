from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Task
from .forms import TaskForm, TaskFilterForm
from projects.models import Project, ProjectActivity
from comments.models import Comment
from comments.forms import CommentForm


@login_required
def task_list_view(request):
    user = request.user
    form = TaskFilterForm(request.GET)

    if user.is_admin:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(assigned_user=user)
        ).distinct()

    tasks = tasks.select_related('project', 'assigned_user', 'created_by')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        assigned = form.cleaned_data.get('assigned_user')
        sort = form.cleaned_data.get('sort', '-created_at')

        if q:
            tasks = tasks.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if status:
            tasks = tasks.filter(status=status)
        if priority:
            tasks = tasks.filter(priority=priority)
        if assigned:
            tasks = tasks.filter(assigned_user=assigned)
        if sort:
            tasks = tasks.order_by(sort)

    return render(request, 'tasks/task_list.html', {'tasks': tasks, 'form': form})


@login_required
def task_detail_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    if not project.user_can_access(request.user):
        messages.error(request, 'Access denied.')
        return redirect('task_list')

    comments = task.comments.select_related('user').order_by('created_at')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            ProjectActivity.objects.create(
                project=project, user=request.user,
                action=f'Commented on task "{task.title}".'
            )
            messages.success(request, 'Comment added.')
            return redirect('task_detail', pk=pk)

    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
        'status_choices': Task.STATUS_CHOICES,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_create_view(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if not project.user_can_access(request.user):
        messages.error(request, 'Access denied.')
        return redirect('project_list')
    if not (project.user_can_manage(request.user) or request.user.is_manager):
        messages.error(request, 'You do not have permission to create tasks.')
        return redirect('project_detail', pk=project_pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            ProjectActivity.objects.create(
                project=project, user=request.user,
                action=f'Task "{task.title}" was created.'
            )
            messages.success(request, f'Task "{task.title}" created.')
            return redirect('project_detail', pk=project_pk)
    else:
        form = TaskForm(project=project)

    return render(request, 'tasks/task_form.html', {
        'form': form, 'project': project, 'action': 'Create'
    })


@login_required
def task_edit_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    can_edit = (
        project.user_can_manage(request.user) or
        task.assigned_user == request.user or
        request.user.is_admin
    )
    if not can_edit:
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('task_detail', pk=pk)

    if request.method == 'POST':
        old_status = task.status
        form = TaskForm(request.POST, instance=task, project=project)
        if form.is_valid():
            task = form.save()
            if old_status != task.status:
                ProjectActivity.objects.create(
                    project=project, user=request.user,
                    action=f'Task "{task.title}" moved to {task.get_status_display()}.'
                )
            else:
                ProjectActivity.objects.create(
                    project=project, user=request.user,
                    action=f'Task "{task.title}" was updated.'
                )
            messages.success(request, 'Task updated.')
            return redirect('task_detail', pk=pk)
    else:
        form = TaskForm(instance=task, project=project)

    return render(request, 'tasks/task_form.html', {
        'form': form, 'task': task, 'project': project, 'action': 'Edit'
    })


@login_required
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    if not project.user_can_manage(request.user):
        messages.error(request, 'You do not have permission to delete this task.')
        return redirect('task_detail', pk=pk)

    if request.method == 'POST':
        title = task.title
        project_pk = project.pk
        ProjectActivity.objects.create(
            project=project, user=request.user,
            action=f'Task "{title}" was deleted.'
        )
        task.delete()
        messages.success(request, f'Task "{title}" deleted.')
        return redirect('project_detail', pk=project_pk)

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
@require_POST
def task_update_status_view(request, pk):
    """AJAX endpoint to quickly update task status."""
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    can_update = (
        project.user_can_access(request.user) and
        (task.assigned_user == request.user or project.user_can_manage(request.user) or request.user.is_admin)
    )
    if not can_update:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    new_status = request.POST.get('status')
    valid_statuses = [s[0] for s in Task.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    old_status = task.status
    task.status = new_status
    task.save()

    ProjectActivity.objects.create(
        project=project, user=request.user,
        action=f'Task "{task.title}" moved from {old_status} → {new_status}.'
    )

    return JsonResponse({
        'status': task.status,
        'status_display': task.get_status_display(),
        'status_color': task.status_color,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
    })


@login_required
def my_tasks_view(request):
    tasks = Task.objects.filter(
        assigned_user=request.user
    ).select_related('project').order_by('deadline', '-priority')

    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    return render(request, 'tasks/my_tasks.html', {
        'tasks': tasks,
        'status_filter': status_filter,
        'status_choices': Task.STATUS_CHOICES,
    })
