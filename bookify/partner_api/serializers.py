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

class ShopSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopSlot
        fields = ['monday_start', 'monday_end', 'tuesday_start', 'tuesday_end',
                 'wednesday_start', 'wednesday_end', 'thursday_start', 'thursday_end',
                 'friday_start', 'friday_end', 'saturday_start', 'saturday_end',
                 'sunday_start', 'sunday_end', 'slot_interval', 'prebooking_rule']