from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'provider', 'date', 'start_time', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['customer__user__username', 'provider__user__username', 'purpose']
    actions = ['approve_appointments', 'reject_appointments']
    
    def approve_appointments(self, request, queryset):
        queryset.update(status=Appointment.APPROVED)
    approve_appointments.short_description = "Approve selected appointments"
    
    def reject_appointments(self, request, queryset):
        queryset.update(status=Appointment.REJECTED)
    reject_appointments.short_description = "Reject selected appointments"