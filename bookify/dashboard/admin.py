from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from dashboard.models import *

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'name', 'phone', 'user_type', 'is_staff', 'created')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_deleted')
    search_fields = ('username', 'name', 'phone')
    ordering = ('-created',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'phone', 'image')}),
        (_('Permissions'), {
            'fields': ('user_type', 'is_staff', 'is_superuser', 'is_deleted', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('created',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'name', 'phone', 'user_type'),
        }),
    )
    readonly_fields = ('created',)
    
    # Override UserAdmin's default attributes
    filter_horizontal = ('groups', 'user_permissions',)
    
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ServiceCategory)
admin.site.register(ServiceProvider)
admin.site.register(Service)
admin.site.register(PaymentMethod)
admin.site.register(Payment)
admin.site.register(Booking)
admin.site.register(UserFavorites)
admin.site.register(Review)