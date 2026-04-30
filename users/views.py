from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from .models import User
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, UserManageForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to TaskHive, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'profile_user': request.user})


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    return render(request, 'users/change_password.html', {'form': form})


@login_required
def user_list_view(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    query = request.GET.get('q', '')
    role = request.GET.get('role', '')
    users = User.objects.all()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) |
                             Q(first_name__icontains=query) | Q(last_name__icontains=query))
    if role:
        users = users.filter(role=role)
    return render(request, 'users/user_list.html', {'users': users, 'query': query, 'selected_role': role})


@login_required
def user_detail_view(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    profile_user = get_object_or_404(User, pk=pk)
    return render(request, 'users/user_detail.html', {'profile_user': profile_user})


@login_required
def user_edit_view(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    profile_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserManageForm(request.POST, instance=profile_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {profile_user.username} updated.')
            return redirect('user_list')
    else:
        form = UserManageForm(instance=profile_user)
    return render(request, 'users/user_edit.html', {'form': form, 'profile_user': profile_user})
