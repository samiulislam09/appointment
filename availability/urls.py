from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'availability'

router = DefaultRouter()
router.register(r'availability', views.AvailabilityViewSet)

urlpatterns = [
    # Web URLs
    path('manage/', views.manage_availability, name='manage'),
    path('delete/<int:pk>/', views.delete_availability, name='delete'),
    
    # API URLs
    path('api/', include(router.urls)),
]