from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import ProviderProfile


class Availability(models.Model):
    """Provider's weekly availability schedule"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    
    WEEKDAY_CHOICES = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    ]
    
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['provider', 'day_of_week', 'start_time', 'end_time']
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
    
    def __str__(self):
        return f"{self.provider.user.username} - {self.get_day_of_week_display()} ({self.start_time}-{self.end_time})"