from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Availability
from .serializers import AvailabilitySerializer
from accounts.models import User


@login_required
def manage_availability(request):
    """Provider availability management view"""
    if request.user.role != User.PROVIDER:
        messages.error(request, 'Only providers can manage availability.')
        return redirect('dashboard:home')
    
    provider = request.user.provider_profile
    availabilities = Availability.objects.filter(provider=provider)
    
    if request.method == 'POST':
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        try:
            Availability.objects.create(
                provider=provider,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, 'Availability added successfully!')
            return redirect('availability:manage')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    weekdays = Availability.WEEKDAY_CHOICES
    return render(request, 'availability/manage.html', {
        'availabilities': availabilities,
        'weekdays': weekdays
    })


@login_required
def delete_availability(request, pk):
    """Delete availability slot"""
    try:
        availability = Availability.objects.get(pk=pk, provider=request.user.provider_profile)
        availability.delete()
        messages.success(request, 'Availability deleted successfully!')
    except Availability.DoesNotExist:
        messages.error(request, 'Availability not found.')
    
    return redirect('availability:manage')


# API ViewSet
class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.filter(is_active=True)
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        provider_id = self.request.query_params.get('provider', None)
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_availability(self, request):
        if request.user.role != User.PROVIDER:
            return Response({'error': 'Only providers can view their availability'}, status=400)
        
        availabilities = Availability.objects.filter(provider=request.user.provider_profile)
        serializer = self.get_serializer(availabilities, many=True)
        return Response(serializer.data)