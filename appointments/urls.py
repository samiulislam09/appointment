from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'appointments'

router = DefaultRouter()
router.register(r'appointments', views.AppointmentViewSet)

urlpatterns = [
    # Web URLs
    path('', views.appointment_list, name='list'),
    path('create/', views.appointment_create, name='create'),
    path('<int:pk>/', views.appointment_detail, name='detail'),
    path('<int:pk>/status/<str:new_status>/', views.appointment_update_status, name='update_status'),
    path('<int:pk>/reschedule/', views.appointment_reschedule, name='reschedule'),
    
    # API URLs
    path('api/', include(router.urls)),
]