# File: stationary/urls.py
"""
URL configuration for stationary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from store import views as store_views
from django.conf.urls import handler404

urlpatterns = [
    path('scribi-secure-admin-panel-9051/', admin.site.urls),

    # Authentication at the root
    path('login/',
         auth_views.LoginView.as_view(template_name='store/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(next_page='store:home'),
         name='logout'),
    path('signup/',
         store_views.signup,
         name='signup'),

    # All your store’s other routes
    path('', include('store.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = store_views.custom_404_view