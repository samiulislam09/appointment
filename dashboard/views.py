from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from appointments.models import Appointment
from accounts.models import User, CustomerProfile, ProviderProfile


@login_required
def dashboard_home(request):
    """Main dashboard view"""
    user = request.user
    context = {}
    
    if user.role == User.PROVIDER:
        # Get or create provider profile
        provider, created = ProviderProfile.objects.get_or_create(
            user=user,
            defaults={'specialization': 'General'}
        )
        
        # Get appointments statistics
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        context.update({
            'total_appointments': Appointment.objects.filter(provider=provider).count(),
            'pending_appointments': Appointment.objects.filter(
                provider=provider, 
                status=Appointment.PENDING
            ).count(),
            'upcoming_appointments': Appointment.objects.filter(
                provider=provider,
                date__gte=today,
                status=Appointment.APPROVED
            ).order_by('date', 'start_time')[:5],
            'this_week_appointments': Appointment.objects.filter(
                provider=provider,
                date__range=[week_start, week_end]
            ).count(),
        })
        
        return render(request, 'dashboard/provider.html', context)
    
    else:
        # Get or create customer profile
        customer, created = CustomerProfile.objects.get_or_create(
            user=user,
            defaults={'company': ''}
        )
        
        today = timezone.now().date()
        
        context.update({
            'total_appointments': Appointment.objects.filter(customer=customer).count(),
            'upcoming_appointments': Appointment.objects.filter(
                customer=customer,
                date__gte=today,
                status__in=[Appointment.PENDING, Appointment.APPROVED]
            ).order_by('date', 'start_time')[:5],
            'past_appointments': Appointment.objects.filter(
                customer=customer,
                date__lt=today
            ).order_by('-date', '-start_time')[:5],
        })
        
        return render(request, 'dashboard/customer.html', context)