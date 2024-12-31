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
from dashboard.views import authentication, users, service_category, booking,shop

urlpatterns = [
    path("", authentication.login, name = 'dashboard-login'),
    path("home/", authentication.home, name = 'dashboard-home'),
    path('users/', users.user_manager, name = "dashboard-user-manager"),
    path('users/list/', users.users_list, name = 'dashboard-users-list'),
    path('users/<int:user_id>/', users.user_detail_view, name='dashboard-user-detail'),
    path('service-categories/', service_category.service_category_manager, name='dashboard-service-category-manager'),
    path('service-categories/list/', service_category.service_category_list, name='dashboard-service-categories-list'),
    path('service-categories/add/', service_category.service_category_add, name='dashboard-service-categories-add'),
    path('service-categories/edit/<int:pk>/', service_category.service_category_edit, name='dashboard-service-categories-edit'),
    path('service-categories/delete/<int:pk>/', service_category.service_category_delete, name='dashboard-service-categories-delete'),
    path('bookings/', booking.booking_manager, name='dashboard-booking-manager'),
    path('bookings/list/', booking.booking_list, name='dashboard-booking-list'),
    path('bookings/<int:pk>/view/', booking.booking_view, name='dashboard-booking-view'),
    path('bookings/<int:pk>/update-status/', booking.update_booking_status, name='dashboard-booking-update-status'),
    path('shops/', shop.manage_shops, name='dashboard-shop-manager'),
    path('shops/list/', shop.shop_list, name='dashboard-shop-list'),
    path('shops/view/<int:pk>/', shop.shop_details, name='dashboard-shop-view'),
    path('shops/edit/<int:pk>/', shop.edit_shop, name='dashboard-shop-edit'),
    path('update_provider/<int:pk>/', shop.update_provider, name='update_provider'),
    path('delete_provider/<int:pk>/', shop.delete_provider, name='delete_provider'),
    path('toggle_provider_verification/<int:pk>/', shop.toggle_provider_verification, name='toggle_provider_verification'),
   
]
