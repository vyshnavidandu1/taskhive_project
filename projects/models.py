from django.db import models
from django.conf import settings
from django.utils import timezone


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMembership',
        related_name='member_projects',
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.name

    @property
    def total_tasks(self):
        return self.tasks.count()

    @property
    def completed_tasks(self):
        return self.tasks.filter(status='completed').count()

    @property
    def progress_percentage(self):
        total = self.total_tasks
        if total == 0:
            return 0
        return int((self.completed_tasks / total) * 100)

    @property
    def is_overdue(self):
        if self.end_date and self.status not in ('completed', 'cancelled'):
            return self.end_date < timezone.now().date()
        return False

    @property
    def days_remaining(self):
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return delta.days
        return None

    def get_all_members(self):
        """Returns owner + team members."""
        from users.models import User
        member_ids = list(self.team_members.values_list('id', flat=True))
        member_ids.append(self.owner_id)
        return User.objects.filter(id__in=member_ids).distinct()

    def user_can_access(self, user):
        if user.is_admin:
            return True
        if self.owner == user:
            return True
        return self.team_members.filter(id=user.id).exists()

    def user_can_manage(self, user):
        if user.is_admin:
            return True
        if self.owner == user:
            return True
        membership = self.memberships.filter(user=user).first()
        return membership and membership.role == 'manager'


class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')
        verbose_name = 'Project Membership'
        verbose_name_plural = 'Project Memberships'

    def __str__(self):
        return f"{self.user.username} – {self.project.name} ({self.get_role_display()})"


class ProjectActivity(models.Model):
    """Tracks all actions within a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name}: {self.action}"
