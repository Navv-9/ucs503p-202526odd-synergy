# from django.urls import path
# from .views import service_list

# urlpatterns = [
#     path("category/<int:category_id>/", service_list),
# ]

from django.urls import path
from .views import ProviderListView, TrustedByFriendsView

urlpatterns = [
    path("providers/", ProviderListView.as_view(), name="provider-list"),
    path("providers/<int:provider_id>/trusted/", TrustedByFriendsView.as_view(), name="trusted-by-friends"),
]