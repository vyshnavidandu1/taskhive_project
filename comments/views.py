from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Comment


@login_required
@require_POST
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    task_pk = comment.task.pk
    if comment.user == request.user or request.user.is_admin:
        comment.delete()
        messages.success(request, 'Comment deleted.')
    else:
        messages.error(request, 'Permission denied.')
    return redirect('task_detail', pk=task_pk)


@login_required
@require_POST
def comment_edit_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user and not request.user.is_admin:
        messages.error(request, 'Permission denied.')
        return redirect('task_detail', pk=comment.task.pk)
    new_message = request.POST.get('message', '').strip()
    if new_message:
        comment.message = new_message
        comment.is_edited = True
        comment.save()
        messages.success(request, 'Comment updated.')
    return redirect('task_detail', pk=comment.task.pk)
