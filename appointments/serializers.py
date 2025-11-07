from rest_framework import serializers
from .models import Appointment
from accounts.serializers import CustomerProfileSerializer, ProviderProfileSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    customer_details = CustomerProfileSerializer(source='customer', read_only=True)
    provider_details = ProviderProfileSerializer(source='provider', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'customer', 'customer_details', 'provider', 'provider_details', 
                  'date', 'start_time', 'end_time', 'purpose', 'status', 'status_display', 
                  'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']