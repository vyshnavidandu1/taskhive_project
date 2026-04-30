from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/password/', views.change_password_view, name='change_password'),
    path('manage/', views.user_list_view, name='user_list'),
    path('manage/<int:pk>/', views.user_detail_view, name='user_detail'),
    path('manage/<int:pk>/edit/', views.user_edit_view, name='user_edit'),
]
