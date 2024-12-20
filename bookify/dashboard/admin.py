from django.contrib import admin
from dashboard.models import *

class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'name', 'email', 'phone')
    ordering = ('-created',)
    
admin.site.register(CustomUser,CustomUserAdmin)