from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='home'),
    path('dashboard/', include('projects.urls_dashboard')),
    path('users/', include('users.urls')),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('comments/', include('comments.urls')),
    path('api/', include('projects.api_urls')),
    path('api/', include('tasks.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
