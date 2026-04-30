from rest_framework import serializers, generics, permissions
from django.db.models import Q
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    progress = serializers.IntegerField(source='progress_percentage', read_only=True)
    total_tasks = serializers.IntegerField(read_only=True)
    completed_tasks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'status', 'owner_name',
                  'start_date', 'end_date', 'created_at', 'progress',
                  'total_tasks', 'completed_tasks')

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username


class ProjectListAPIView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Project.objects.all()
        return Project.objects.filter(
            Q(owner=user) | Q(team_members=user)
        ).distinct()


class ProjectDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Project.objects.all()
        return Project.objects.filter(
            Q(owner=user) | Q(team_members=user)
        ).distinct()
