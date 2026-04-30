from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list_view, name='task_list'),
    path('my/', views.my_tasks_view, name='my_tasks'),
    path('<int:pk>/', views.task_detail_view, name='task_detail'),
    path('<int:pk>/edit/', views.task_edit_view, name='task_edit'),
    path('<int:pk>/delete/', views.task_delete_view, name='task_delete'),
    path('<int:pk>/status/', views.task_update_status_view, name='task_update_status'),
    path('project/<int:project_pk>/create/', views.task_create_view, name='task_create'),
]
