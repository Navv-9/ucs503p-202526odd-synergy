from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('service/<str:category_name>/', views.service_providers, name='service_providers'),
    path('provider/<int:provider_id>/', views.provider_detail, name='provider_detail'),
    path('populate-data/', views.populate_fake_data, name='populate_data'),
]