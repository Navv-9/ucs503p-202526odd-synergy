from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Home - /
    path('', views.home, name='home'),
    
    # Auth routes - /api/...
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login, name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', views.get_user_profile, name='user_profile'),
    
    # Service routes - /service/...
    path('service/<str:category_name>/', views.service_providers, name='service_providers'),
    path('provider/<str:provider_id>/', views.provider_detail, name='provider_detail'),
    
    # Booking routes - /api/bookings/...
    path('api/bookings/create/', views.create_booking, name='create_booking'),
    path('api/bookings/', views.get_user_bookings, name='user_bookings'),
    path('api/bookings/<str:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Review routes - /api/provider/<id>/review/
    path('api/provider/<str:provider_id>/review/', views.submit_review, name='submit_review'),
    
    # Provider Registration - /api/provider/register/
    path('api/provider/register/', views.provider_register, name='provider_register'),
    
    # Provider Dashboard & Profile - /api/provider/...
    path('api/provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('api/provider/profile/', views.provider_profile, name='provider_profile'),
    
    # Provider Bookings Management - /api/provider/bookings/...
    path('api/provider/bookings/', views.provider_bookings, name='provider_bookings'),
    path('api/provider/bookings/<str:booking_id>/accept/', views.provider_accept_booking, name='provider_accept_booking'),
    path('api/provider/bookings/<str:booking_id>/reject/', views.provider_reject_booking, name='provider_reject_booking'),
    path('api/provider/bookings/<str:booking_id>/complete/', views.provider_complete_booking, name='provider_complete_booking'),
    
    # Provider Reviews - /api/provider/reviews/
    path('api/provider/reviews/', views.provider_reviews, name='provider_reviews'),
    
    # Test data - /populate-data/
    path('populate-data/', views.populate_fake_data, name='populate_data'),

    path('debug/urls/', views.list_urls, name='list_urls'),
]