from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/delete/', views.comment_delete_view, name='comment_delete'),
    path('<int:pk>/edit/', views.comment_edit_view, name='comment_edit'),
]
