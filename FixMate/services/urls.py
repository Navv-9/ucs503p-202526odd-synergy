from django.urls import path
from .views import service_list

urlpatterns = [
    path("category/<int:category_id>/", service_list),
]
