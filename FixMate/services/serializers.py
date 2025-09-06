# from rest_framework import serializers
# from .models import ServiceProvider, ServiceCategory

# class ServiceProviderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServiceProvider
#         fields = "__all__"


# class ServiceCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServiceCategory
#         fields = "__all__"


from rest_framework import serializers
from .models import User, ServiceProvider, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "trusted", "comment"]


class ServiceProviderSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceProvider
        fields = ["id", "name", "service_type", "contact_info", "reviews"]