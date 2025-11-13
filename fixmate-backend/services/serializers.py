from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, ServiceCategory, ServiceProvider, Review, Booking
import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'user_type', 'is_provider']
    
    def get_username(self, obj):
        try:
            user = User.objects.get(id=obj.user_id)
            return user.username
        except User.DoesNotExist:
            return ""
    
    def get_email(self, obj):
        try:
            user = User.objects.get(id=obj.user_id)
            return user.email
        except User.DoesNotExist:
            return ""
    
    def get_first_name(self, obj):
        try:
            user = User.objects.get(id=obj.user_id)
            return user.first_name
        except User.DoesNotExist:
            return ""
    
    def get_last_name(self, obj):
        try:
            user = User.objects.get(id=obj.user_id)
            return user.last_name
        except User.DoesNotExist:
            return ""


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm Password')
    phone_number = serializers.CharField(required=True, max_length=15)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone_number']
    
    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def validate_email(self, value):
        """Check if email already exists"""
        if not value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def validate_phone_number(self, value):
        """Check if phone number already exists"""
        if UserProfile.objects.filter(phone_number=value).exists():
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
        
        # CRITICAL FIX: Get the actual integer ID from database
        # Query the user back to get the real ID Django assigned
        user = User.objects.get(username=user.username)
        
        # Now user.id or user.pk will be the actual integer from database
        if hasattr(user.pk, 'binary'):
            # If it's still ObjectId, convert to integer
            from bson import ObjectId
            if isinstance(user.pk, ObjectId):
                # Store ObjectId as string, then convert to consistent integer
                user_id_for_storage = int(str(user.pk)[-9:], 16)  # Last 9 hex chars as int
            else:
                user_id_for_storage = int(user.pk)
        else:
            user_id_for_storage = int(user.pk)
        
        logger.info(f"Created user with ID: {user_id_for_storage} (type: {type(user_id_for_storage)})")
        
        # Create profile with the integer ID
        profile = UserProfile(
            user_id=user_id_for_storage,
            phone_number=phone_number
        )
        profile.save()
        
        return user


class BookingSerializer(serializers.ModelSerializer):
    provider_id = serializers.CharField(max_length=24)
    user_name = serializers.SerializerMethodField(read_only=True)
    provider_name = serializers.SerializerMethodField(read_only=True)
    provider_category = serializers.SerializerMethodField(read_only=True)
    provider_phone = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'user_id', 'user_name', 'provider_id', 'provider_name',
                  'provider_category', 'provider_phone', 'booking_date', 'booking_time', 
                  'status', 'notes', 'created_at']
        read_only_fields = ['user_id', 'created_at', 'status']
    
    def get_user_name(self, obj):
        """Get username from user_id"""
        try:
            user = User.objects.get(id=obj.user_id)
            return user.username
        except User.DoesNotExist:
            return "Unknown"
    
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


class ProviderRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    category_name = serializers.CharField(required=True)
    experience_years = serializers.IntegerField(required=True)
    service_area = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    availability = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 
                  'phone_number', 'category_name', 'experience_years', 'service_area', 'city', 
                  'description', 'availability']
    
    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def validate_email(self, value):
        """Check if email already exists"""
        if not value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def validate_phone_number(self, value):
        """Check if phone number already exists"""
        if UserProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs
    
    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        
        # Extract provider fields
        phone_number = validated_data.pop('phone_number')
        category_name = validated_data.pop('category_name')
        experience_years = validated_data.pop('experience_years')
        service_area = validated_data.pop('service_area')
        city = validated_data.pop('city')
        description = validated_data.pop('description', '')
        availability = validated_data.pop('availability', 'Mon-Sat, 9AM-6PM')
        validated_data.pop('password2')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                password=validated_data['password']
            )
            
            # CRITICAL FIX: Query user back to get actual ID
            user = User.objects.get(username=user.username)
            
            # Convert to integer (handle ObjectId case)
            if hasattr(user.pk, 'binary'):
                from bson import ObjectId
                if isinstance(user.pk, ObjectId):
                    user_id_for_storage = int(str(user.pk)[-9:], 16)
                else:
                    user_id_for_storage = int(user.pk)
            else:
                user_id_for_storage = int(user.pk)
            
            logger.info(f"✅ Provider user created with ID: {user_id_for_storage} (type: {type(user_id_for_storage)})")
            
            # Create user profile
            profile = UserProfile(
                user_id=user_id_for_storage,
                phone_number=phone_number,
                user_type='provider',
                is_provider=True
            )
            profile.save()
            logger.info(f"✅ UserProfile created with user_id: {profile.user_id}")
            
            # Create service provider profile
            provider = ServiceProvider(
                user_id=user_id_for_storage,
                name=f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                phone_number=phone_number,
                email=user.email,
                category_name=category_name,
                experience_years=experience_years,
                address=service_area,
                service_area=service_area,
                city=city,
                description=description,
                availability=availability,
                rating=0.0,
                original_rating=0.0,
                total_reviews=0
            )
            provider.save()
            logger.info(f"✅ ServiceProvider created with user_id: {provider.user_id}")
            
            return user
            
        except Exception as e:
            logger.error(f"❌ Error during provider registration: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Clean up if something failed
            if 'user' in locals():
                try:
                    user.delete()
                except:
                    pass
            raise


class ServiceProviderSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceProvider
        fields = ['id', 'name', 'phone_number', 'email', 'category_name', 
                  'experience_years', 'address', 'service_area', 'city', 'description', 
                  'availability', 'rating', 'total_reviews', 'is_verified', 
                  'is_active', 'joined_date']
    
    def get_id(self, obj):
        return str(obj._id) if obj._id else None


class ProviderBookingSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField(read_only=True)
    customer_phone = serializers.SerializerMethodField()
    customer_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'customer_name', 'customer_phone', 'customer_address',
                  'booking_date', 'booking_time', 'status', 'provider_status',
                  'notes', 'completion_notes', 'created_at', 'completed_at']
    
    def get_id(self, obj):
        return str(obj._id) if obj._id else None
    
    def get_customer_name(self, obj):
        """Get customer name from user_id"""
        try:
            user = User.objects.get(id=obj.user_id)
            return user.username
        except User.DoesNotExist:
            return "Unknown"
    
    def get_customer_phone(self, obj):
        try:
            profile = UserProfile.objects.get(user_id=obj.user_id)
            return profile.phone_number
        except:
            return ""
    
    def get_customer_address(self, obj):
        try:
            profile = UserProfile.objects.get(user_id=obj.user_id)
            return profile.address
        except:
            return ""