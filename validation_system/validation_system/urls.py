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
    # path('', views.upload_file, name='upload_file'),
    path('dashboard/', views.verify, name='verify'),
    path('', views.varified_db, name='varified_db'),
    path('', views.unvarified_db, name='unvarified_db'),
    path('', views.your_view_name, name='your_view_name'),
    # path('', views.get_request, name='get_request'),
]