# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import ServiceProvider
# from users.models import Review

# @api_view(["GET"])
# def service_list(request, category_id):
#     user = request.user  # assuming user is logged in
#     providers = ServiceProvider.objects.filter(category_id=category_id)

#     data = []
#     for provider in providers:
#         reviews = Review.objects.filter(service_provider=provider, thumbs_up=True, user__in=user.contacts.all())
#         trusted_by = [r.user.username for r in reviews]
#         data.append({
#             "provider": provider.name,
#             "contact": provider.contact_info,
#             "trusted_by": trusted_by
#         })
#     return Response(data)


from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ServiceProvider, Review
from .serializers import ServiceProviderSerializer


# ✅ API: List all providers with normal details
class ProviderListView(generics.ListAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [permissions.AllowAny]


# ✅ API: Trusted by my friends
# class TrustedByFriendsView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, provider_id):
#         user = request.user
#         provider = ServiceProvider.objects.get(id=provider_id)

#         # get my friends
#         friends = user.contacts.all()

#         # get reviews where reviewer is in my friends and trusted=True
#         trusted_reviews = Review.objects.filter(
#             provider=provider,
#             user__in=friends,
#             trusted=True
#         )

#         data = {
#             "provider": provider.name,
#             "trusted_by": [review.user.username for review in trusted_reviews]
#         }
#         return Response(data)

class TrustedByFriendsView(APIView):
    permission_classes = [permissions.AllowAny]  # dev only

    def get(self, request, provider_id):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"trusted_by": []})

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(id=int(user_id))
        except User.DoesNotExist:
            return Response({"trusted_by": []})

        provider = ServiceProvider.objects.get(id=provider_id)
        friends = user.contacts.all()
        trusted_reviews = Review.objects.filter(provider=provider, user__in=friends, trusted=True)

        return Response({
            "provider": provider.name,
            "trusted_by": [r.user.username for r in trusted_reviews]
        })