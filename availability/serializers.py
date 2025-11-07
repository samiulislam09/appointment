from rest_framework import serializers
from .models import Availability


class AvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = Availability
        fields = ['id', 'provider', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_active']
        read_only_fields = ['id']