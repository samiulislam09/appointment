from rest_framework import serializers
from .models import User, ProviderProfile, CustomerProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone']
        read_only_fields = ['id']


class ProviderProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ProviderProfile
        fields = ['id', 'user', 'specialization', 'bio', 'is_approved', 'created_at']


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'company', 'created_at']