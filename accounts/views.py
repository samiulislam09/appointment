from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, ProviderProfile, CustomerProfile
from .forms import UserRegistrationForm, ProviderProfileForm, CustomerProfileForm
from .serializers import UserSerializer, ProviderProfileSerializer, CustomerProfileSerializer


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create profile based on role
            if user.role == User.PROVIDER:
                ProviderProfile.objects.get_or_create(
                    user=user,
                    defaults={'specialization': 'General', 'bio': ''}
                )
            else:
                CustomerProfile.objects.get_or_create(
                    user=user,
                    defaults={'company': ''}
                )
            
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Ensure profile exists
            if user.role == User.PROVIDER:
                ProviderProfile.objects.get_or_create(
                    user=user,
                    defaults={'specialization': 'General', 'bio': ''}
                )
            else:
                CustomerProfile.objects.get_or_create(
                    user=user,
                    defaults={'company': ''}
                )
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    
    if user.role == User.PROVIDER:
        profile, created = ProviderProfile.objects.get_or_create(
            user=user,
            defaults={'specialization': 'General', 'bio': ''}
        )
        if request.method == 'POST':
            form = ProviderProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
        else:
            form = ProviderProfileForm(instance=profile)
    else:
        profile, created = CustomerProfile.objects.get_or_create(
            user=user,
            defaults={'company': ''}
        )
        if request.method == 'POST':
            form = CustomerProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
        else:
            form = CustomerProfileForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


# API ViewSets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ProviderProfileViewSet(viewsets.ModelViewSet):
    queryset = ProviderProfile.objects.filter(is_approved=True)
    serializer_class = ProviderProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        specialization = self.request.query_params.get('specialization', None)
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        return queryset