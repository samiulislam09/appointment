import sys
import os

path = '/home/yourusername/appointment'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'appointment.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Appointment
from .forms import AppointmentForm
from .serializers import AppointmentSerializer
from accounts.models import User, ProviderProfile
from datetime import datetime, timedelta


@login_required
def appointment_list(request):
    """List all appointments for the user"""
    if request.user.role == User.PROVIDER:
        appointments = Appointment.objects.filter(provider=request.user.provider_profile)
    else:
        appointments = Appointment.objects.filter(customer=request.user.customer_profile)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    return render(request, 'appointments/list.html', {
        'appointments': appointments,
        'status_choices': Appointment.STATUS_CHOICES
    })


@login_required
def appointment_create(request):
    """Create a new appointment"""
    if request.user.role != User.CUSTOMER:
        messages.error(request, 'Only customers can book appointments.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user.customer_profile
            
            # Validate the appointment
            try:
                appointment.clean()
                appointment.save()
                messages.success(request, 'Appointment booked successfully! Waiting for provider approval.')
                return redirect('appointments:detail', pk=appointment.pk)
            except ValidationError as e:
                # Add validation errors to the form
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field if field != '__all__' else None, error)
                messages.error(request, 'Please correct the errors below.')
            except Exception as e:
                messages.error(request, f'Error booking appointment: {str(e)}')
                form.add_error(None, str(e))
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()
    
    providers = ProviderProfile.objects.filter(is_approved=True)
    return render(request, 'appointments/create.html', {
        'form': form,
        'providers': providers
    })


@login_required
def appointment_detail(request, pk):
    """View appointment details"""
    if request.user.role == User.PROVIDER:
        appointment = get_object_or_404(Appointment, pk=pk, provider=request.user.provider_profile)
    else:
        appointment = get_object_or_404(Appointment, pk=pk, customer=request.user.customer_profile)
    
    return render(request, 'appointments/detail.html', {'appointment': appointment})


@login_required
def appointment_update_status(request, pk, new_status):
    """Update appointment status (approve/reject/complete/cancel)"""
    if request.user.role == User.PROVIDER:
        appointment = get_object_or_404(Appointment, pk=pk, provider=request.user.provider_profile)
        if new_status in [Appointment.APPROVED, Appointment.REJECTED, Appointment.COMPLETED]:
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Appointment {new_status} successfully!')
        else:
            messages.error(request, 'Invalid status.')
    else:
        appointment = get_object_or_404(Appointment, pk=pk, customer=request.user.customer_profile)
        if new_status == Appointment.CANCELLED:
            appointment.status = new_status
            appointment.save()
            messages.success(request, 'Appointment cancelled successfully!')
        else:
            messages.error(request, 'You can only cancel appointments.')
    
    return redirect('appointments:detail', pk=pk)


@login_required
def appointment_reschedule(request, pk):
    """Reschedule an appointment"""
    if request.user.role == User.CUSTOMER:
        appointment = get_object_or_404(Appointment, pk=pk, customer=request.user.customer_profile)
    else:
        messages.error(request, 'Only customers can reschedule appointments.')
        return redirect('appointments:list')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            try:
                updated_appointment = form.save(commit=False)
                updated_appointment.clean()
                updated_appointment.status = Appointment.PENDING
                updated_appointment.save()
                messages.success(request, 'Appointment rescheduled successfully! Waiting for provider approval.')
                return redirect('appointments:detail', pk=pk)
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field if field != '__all__' else None, error)
                messages.error(request, 'Please correct the errors below.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
                form.add_error(None, str(e))
    else:
        form = AppointmentForm(instance=appointment)
    
    return render(request, 'appointments/reschedule.html', {
        'form': form,
        'appointment': appointment
    })


# API ViewSet
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == User.PROVIDER:
            return Appointment.objects.filter(provider=user.provider_profile)
        else:
            return Appointment.objects.filter(customer=user.customer_profile)
    
    def perform_create(self, serializer):
        if self.request.user.role != User.CUSTOMER:
            raise ValueError('Only customers can create appointments')
        serializer.save(customer=self.request.user.customer_profile)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        appointment = self.get_object()
        if request.user.role != User.PROVIDER:
            return Response({'error': 'Only providers can approve'}, status=400)
        
        appointment.status = Appointment.APPROVED
        appointment.save()
        return Response({'status': 'approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        appointment = self.get_object()
        if request.user.role != User.PROVIDER:
            return Response({'error': 'Only providers can reject'}, status=400)
        
        appointment.status = Appointment.REJECTED
        appointment.save()
        return Response({'status': 'rejected'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        if request.user.role != User.PROVIDER:
            return Response({'error': 'Only providers can complete'}, status=400)
        
        appointment.status = Appointment.COMPLETED
        appointment.save()
        return Response({'status': 'completed'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if request.user.role != User.CUSTOMER:
            return Response({'error': 'Only customers can cancel'}, status=400)
        
        appointment.status = Appointment.CANCELLED
        appointment.save()
        return Response({'status': 'cancelled'})