from django.urls import path
from .api_views import ProjectListAPIView, ProjectDetailAPIView

urlpatterns = [
    path('projects/', ProjectListAPIView.as_view(), name='api_project_list'),
    path('projects/<int:pk>/', ProjectDetailAPIView.as_view(), name='api_project_detail'),
]
