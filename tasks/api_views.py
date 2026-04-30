from rest_framework import serializers, generics, permissions
from django.db.models import Q
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    assigned_user_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'project', 'project_name',
                  'assigned_user', 'assigned_user_name', 'priority', 'priority_display',
                  'status', 'status_display', 'deadline', 'created_at', 'is_overdue')

    def get_assigned_user_name(self, obj):
        if obj.assigned_user:
            return obj.assigned_user.get_full_name() or obj.assigned_user.username
        return None

    def get_project_name(self, obj):
        return obj.project.name


class TaskListAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            qs = Task.objects.all()
        else:
            qs = Task.objects.filter(
                Q(project__owner=user) | Q(project__team_members=user) | Q(assigned_user=user)
            ).distinct()
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        return qs.select_related('project', 'assigned_user')


class TaskDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Task.objects.all()
        return Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(assigned_user=user)
        ).distinct()
