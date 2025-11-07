from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended User model with role field"""
    CUSTOMER = 'customer'
    PROVIDER = 'provider'
    
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (PROVIDER, 'Service Provider'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CUSTOMER)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class ProviderProfile(models.Model):
    """Profile for service providers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    specialization = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialization}"


class CustomerProfile(models.Model):
    """Profile for customers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    company = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company}"