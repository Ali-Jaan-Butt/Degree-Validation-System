"""
URL configuration for validation_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.myapp, name='myapp'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('admin-login/', views.login, name='login'),
    path('admin/dashboard/', views.dashboard, name='dashboard'),
    path('admin/admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/saved-template/', views.saved_template, name='saved_template'),
    path('admin/reports/', views.report, name='report'),
    path('admin/settings/', views.settings, name='settings'),
    path('verify/', views.verify, name='verify'),
    path('', views.varified_db, name='varified_db'),
    path('', views.unvarified_db, name='unvarified_db'),
    path('', views.handle_checkbox_form, name='handle_checkbox_form'),
    path('admin/settings/', views.change_username, name='change_username'),
    path('admin.settings/', views.change_password, name='change_password'),
    # path('', views.get_request, name='get_request'),
]