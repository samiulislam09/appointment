from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import CustomerProfile, ProviderProfile


class Appointment(models.Model):
    """Corporate meeting appointment"""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='appointments')
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
    
    def clean(self):
        # Validate time range
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
        
        # Prevent booking in the past
        if self.date < timezone.now().date():
            raise ValidationError("Cannot book appointments in the past")
        
        # Check for overlapping appointments
        if self.pk:
            overlapping = Appointment.objects.filter(
                provider=self.provider,
                date=self.date,
                status__in=[self.PENDING, self.APPROVED]
            ).exclude(pk=self.pk)
        else:
            overlapping = Appointment.objects.filter(
                provider=self.provider,
                date=self.date,
                status__in=[self.PENDING, self.APPROVED]
            )
        
        for appointment in overlapping:
            if (self.start_time < appointment.end_time and 
                self.end_time > appointment.start_time):
                raise ValidationError("This time slot overlaps with an existing appointment")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer.user.username} with {self.provider.user.username} on {self.date}"