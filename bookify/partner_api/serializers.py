from rest_framework import serializers
from dashboard.models import Service, ServiceProvider, ServiceCategory
from django.contrib.auth import get_user_model

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ['shop_name', 'category', 'shop_type', 'address', 'location', 
                 'team_size', 'booking_preferences', 'opening_time', 'closing_time']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration']
