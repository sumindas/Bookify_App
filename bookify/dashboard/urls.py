"""
URL configuration for bookify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from dashboard.views import authentication,users,service_category

urlpatterns = [
    path("", authentication.login, name = 'dashboard-login'),
    path("home/", authentication.home, name = 'dashboard-home'),
    path('user_manager/', users.user_manager, name = "dashboard-user-manager"),
    path('users_list/',users.users_list, name = 'dashboard-users-list'),
    # path('users_view/<int:pk>/',views.user_view, name = 'dashboard-users-view'),
    path('service-categories/', service_category.service_category_manager, name='dashboard-service-category-manager'),
    path('service-categories/list/', service_category.service_category_list, name='dashboard-service-categories-list'),
    path('service-categories/add/', service_category.service_category_add, name='dashboard-service-categories-add'),
    path('service-categories/edit/<int:pk>/', service_category.service_category_edit, name='service_category_edit'),
    
    
    
]
