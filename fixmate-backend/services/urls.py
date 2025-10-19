from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth routes
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login, name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', views.get_user_profile, name='user_profile'),
    
    # Service routes
    path('', views.home, name='home'),
    path('service/<str:category_name>/', views.service_providers, name='service_providers'),
    path('provider/<int:provider_id>/', views.provider_detail, name='provider_detail'),
    
    # Booking routes
    path('api/bookings/create/', views.create_booking, name='create_booking'),
    path('api/bookings/', views.get_user_bookings, name='user_bookings'),
    path('api/bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Test data
    path('populate-data/', views.populate_fake_data, name='populate_data'),
    # Review routes
    path('api/provider/<int:provider_id>/review/', views.submit_review, name='submit_review'),
]