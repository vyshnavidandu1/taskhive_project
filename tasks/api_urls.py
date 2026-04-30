from django.urls import path
from .api_views import TaskListAPIView, TaskDetailAPIView

urlpatterns = [
    path('tasks/', TaskListAPIView.as_view(), name='api_task_list'),
    path('tasks/<int:pk>/', TaskDetailAPIView.as_view(), name='api_task_detail'),
]
