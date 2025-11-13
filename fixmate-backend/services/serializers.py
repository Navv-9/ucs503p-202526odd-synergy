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


def convert_pk_to_user_id(user_pk):
    """
    Centralized function to convert Django user.pk to integer user_id
    This ensures consistency across all registration and authentication
    """
    from bson import ObjectId
    
    logger.info(f"Converting pk: {user_pk} (type: {type(user_pk).__name__})")
    
    # If already an integer, return it
    if isinstance(user_pk, int):
        logger.info(f"✅ Already integer: {user_pk}")
        return user_pk
    
    # If it's an ObjectId
    if isinstance(user_pk, ObjectId):
        user_id = int(str(user_pk)[-9:], 16)
        logger.info(f"✅ Converted ObjectId {user_pk} to {user_id}")
        return user_id
    
    # If it's a string
    if isinstance(user_pk, str):
        # Try to parse as ObjectId
        try:
            oid = ObjectId(user_pk)
            user_id = int(str(oid)[-9:], 16)
            logger.info(f"✅ Converted string ObjectId {user_pk} to {user_id}")
            return user_id
        except:
            pass
        
        # Try direct integer conversion
        try:
            user_id = int(user_pk)
            logger.info(f"✅ Converted string to int: {user_id}")
            return user_id
        except:
            pass
    
    # Last resort: use hash
    user_id = abs(hash(str(user_pk))) % (10 ** 10)
    logger.warning(f"⚠️ Using hash for {user_pk}: {user_id}")
    return user_id


class RegisterSerializer(serializers.ModelSerializer):
    """Customer registration serializer"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm Password')
    phone_number = serializers.CharField(required=True, max_length=15)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone_number']
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def validate_email(self, value):
        if not value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def validate_phone_number(self, value):
        if UserProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        validated_data.pop('password2')
        
        user = None
        profile = None
        
        try:
            # Create user
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                password=validated_data['password']
            )
            
            logger.info(f"✅ User created: {user.username}, pk: {user.pk}")
            
            # Convert user.pk to integer user_id
            user_id = convert_pk_to_user_id(user.pk)
            logger.info(f"✅ Converted to user_id: {user_id}")
            
            # Create profile
            profile = UserProfile.objects.create(
                user_id=user_id,
                phone_number=phone_number,
                user_type='customer',
                is_provider=False
            )
            
            logger.info(f"✅ Customer profile created with user_id: {profile.user_id}")
            
            return user
            
        except Exception as e:
            logger.error(f"❌ Error in customer registration: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            
            import traceback
            logger.error(traceback.format_exc())
            
            # Cleanup on error
            if profile:
                try:
                    profile.delete()
                    logger.info("🧹 Cleaned up profile")
                except:
                    pass
            
            if user:
                try:
                    user.delete()
                    logger.info("🧹 Cleaned up user")
                except:
                    pass
            
            raise serializers.ValidationError(f"Registration failed: {str(e)}")


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
    """Service provider registration serializer"""
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
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def validate_email(self, value):
        if not value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def validate_phone_number(self, value):
        # Check both UserProfile and ServiceProvider
        if UserProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        if ServiceProvider.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered as a provider.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs
    
    def create(self, validated_data):
        # Extract provider-specific fields
        phone_number = validated_data.pop('phone_number')
        category_name = validated_data.pop('category_name')
        experience_years = validated_data.pop('experience_years')
        service_area = validated_data.pop('service_area')
        city = validated_data.pop('city')
        description = validated_data.pop('description', '')
        availability = validated_data.pop('availability', 'Mon-Sat, 9AM-6PM')
        validated_data.pop('password2')
        
        user = None
        profile = None
        provider = None
        
        try:
            # Step 1: Create Django user
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                password=validated_data['password']
            )
            
            logger.info(f"✅ Provider user created: {user.username}, pk: {user.pk}")
            
            # Step 2: Convert user.pk to integer user_id
            user_id = convert_pk_to_user_id(user.pk)
            logger.info(f"✅ Converted to user_id: {user_id}")
            
            # Step 3: Create UserProfile
            profile = UserProfile.objects.create(
                user_id=user_id,
                phone_number=phone_number,
                user_type='provider',
                is_provider=True
            )
            logger.info(f"✅ UserProfile created with user_id: {profile.user_id}")
            
            # Step 4: Create ServiceProvider profile
            provider_name = f"{user.first_name} {user.last_name}".strip() if user.first_name else user.username
            
            provider = ServiceProvider.objects.create(
                user_id=user_id,
                name=provider_name,
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
            logger.info(f"✅ ServiceProvider created:")
            logger.info(f"   - _id: {provider._id}")
            logger.info(f"   - user_id: {provider.user_id}")
            logger.info(f"   - name: {provider.name}")
            logger.info(f"   - category: {provider.category_name}")
            
            # Step 5: Verify everything is linked correctly
            verify_profile = UserProfile.objects.get(user_id=user_id)
            verify_provider = ServiceProvider.objects.get(user_id=user_id)
            
            logger.info(f"✅ VERIFICATION SUCCESSFUL:")
            logger.info(f"   - Django User: {user.username} (pk={user.pk})")
            logger.info(f"   - Converted user_id: {user_id}")
            logger.info(f"   - UserProfile.user_id: {verify_profile.user_id}")
            logger.info(f"   - ServiceProvider.user_id: {verify_provider.user_id}")
            logger.info(f"   - All IDs match: {user_id == verify_profile.user_id == verify_provider.user_id}")
            
            return user
            
        except Exception as e:
            logger.error(f"❌ Error during provider registration: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            
            import traceback
            logger.error(traceback.format_exc())
            
            # Cleanup on error (in reverse order)
            if provider:
                try:
                    provider.delete()
                    logger.info("🧹 Cleaned up ServiceProvider")
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup provider: {cleanup_error}")
            
            if profile:
                try:
                    profile.delete()
                    logger.info("🧹 Cleaned up UserProfile")
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup profile: {cleanup_error}")
            
            if user:
                try:
                    user.delete()
                    logger.info("🧹 Cleaned up User")
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup user: {cleanup_error}")
            
            raise serializers.ValidationError(f"Provider registration failed: {str(e)}")



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