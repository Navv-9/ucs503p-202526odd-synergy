from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, ServiceCategory, ServiceProvider, Review, Booking

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'phone_number', 'address']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm Password')
    phone_number = serializers.CharField(required=True, max_length=15)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone_number']
    
    def validate_username(self, value):
        """Check if username already exists"""
        if len(list(User.objects.filter(username=value))) > 0:
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def validate_email(self, value):
        """Check if email already exists"""
        if value and len(list(User.objects.filter(email=value))) > 0:
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def validate_phone_number(self, value):
        """Check if phone number already exists"""
        if len(list(UserProfile.objects.filter(phone_number=value))) > 0:
            raise serializers.ValidationError("This phone number is already registered.")
        return value
    
    def validate(self, attrs):
        """Check if passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        validated_data.pop('password2')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        
        # CRITICAL: Refresh user from database to get proper ID format
        user.refresh_from_db()
        
        # Create user profile
        UserProfile.objects.create(user=user, phone_number=phone_number)
        
        return user

class BookingSerializer(serializers.ModelSerializer):
    provider_id = serializers.CharField(max_length=24)
    user_name = serializers.CharField(source='user.username', read_only=True)
    provider_name = serializers.SerializerMethodField(read_only=True)
    provider_category = serializers.SerializerMethodField(read_only=True)
    provider_phone = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'user', 'user_name', 'provider_id', 'provider_name', 
                  'provider_category', 'provider_phone', 'booking_date', 'booking_time', 
                  'status', 'notes', 'created_at']
        read_only_fields = ['user', 'created_at', 'status']
    
    def get_provider_name(self, obj):
        """Get provider name from provider_id"""
        from bson import ObjectId
        try:
            provider = ServiceProvider.objects.get(_id=ObjectId(obj.provider_id))
            return provider.name
        except:
            return "Unknown Provider"
    
    def get_provider_category(self, obj):
        """Get provider category from provider_id"""
        from bson import ObjectId
        try:
            provider = ServiceProvider.objects.get(_id=ObjectId(obj.provider_id))
            return provider.category_name
        except:
            return "Unknown"
    
    def get_provider_phone(self, obj):
        """Get provider phone from provider_id"""
        from bson import ObjectId
        try:
            provider = ServiceProvider.objects.get(_id=ObjectId(obj.provider_id))
            return provider.phone_number
        except:
            return ""

    def validate_provider_id(self, value):
        """Validate that provider_id is a valid ObjectId"""
        from bson import ObjectId
        from bson.errors import InvalidId
        try:
            ObjectId(value)
            return value
        except (InvalidId, ValueError):
            raise serializers.ValidationError("Invalid provider ID")
    
    def to_representation(self, instance):
        """Return _id as the id field"""
        representation = super().to_representation(instance)
        if hasattr(instance, '_id') and instance._id:
            representation['id'] = str(instance._id)
        return representation