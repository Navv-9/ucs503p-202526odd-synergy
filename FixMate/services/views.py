from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ServiceProvider
from users.models import Review

@api_view(["GET"])
def service_list(request, category_id):
    user = request.user  # assuming user is logged in
    providers = ServiceProvider.objects.filter(category_id=category_id)

    data = []
    for provider in providers:
        reviews = Review.objects.filter(service_provider=provider, thumbs_up=True, user__in=user.contacts.all())
        trusted_by = [r.user.username for r in reviews]
        data.append({
            "provider": provider.name,
            "contact": provider.contact_info,
            "trusted_by": trusted_by
        })
    return Response(data)
