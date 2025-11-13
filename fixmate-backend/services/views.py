from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from bson import ObjectId
from bson.errors import InvalidId
from .models import ServiceCategory, ServiceProvider, Review, UserProfile, Contact, Booking
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer, BookingSerializer, ProviderRegisterSerializer, ServiceProviderSerializer, ProviderBookingSerializer

# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        # Get user profile - CHANGED: Use user_id
        try:
            profile = UserProfile.objects.get(user_id=user.id)
            user_type = profile.user_type
            is_provider = profile.is_provider
        except UserProfile.DoesNotExist:
            user_type = 'customer'
            is_provider = False
        
        return Response({
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user_type,
                'is_provider': is_provider
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully!'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Please provide both username and password'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        
        # Get user profile to check user type - CHANGED: Use user_id
        try:
            profile = UserProfile.objects.get(user_id=user.id)
            user_type = profile.user_type
            is_provider = profile.is_provider
        except UserProfile.DoesNotExist:
            user_type = 'customer'
            is_provider = False
        
        return Response({
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user_type,
                'is_provider': is_provider
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful!'
        }, status=status.HTTP_200_OK)
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get current user profile"""
    try:
        profile = UserProfile.objects.get(user_id=request.user.id)  # CHANGED
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

# Service Views
@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    """Homepage showing service categories"""
    categories = ServiceCategory.objects.all()
    return JsonResponse({
        'message': 'FixMate API - Service Categories',
        'categories': [
            {
                'id': str(cat.pk),
                'name': cat.name,
                'description': cat.description,
                'icon': cat.icon
            } for cat in categories
        ]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def service_providers(request, category_name):
    """Show providers for a specific service category with social proof"""
    try:
        category = ServiceCategory.objects.get(name__iexact=category_name)
        city_filter = request.GET.get('city', None)
        providers = ServiceProvider.objects.filter(category_name=category_name)
        if city_filter:
            providers = providers.filter(city__iexact=city_filter)

        providers_data = []
        for provider in providers:
            trusted_friends = get_trusted_friends(provider, request)
            
            providers_data.append({
                'id': str(provider._id),
                'name': provider.name,
                'phone': provider.phone_number,
                'email': provider.email,
                'rating': provider.rating,
                'total_reviews': provider.total_reviews,
                'experience_years': provider.experience_years,
                'address': provider.address,
                'city': provider.city,
                'service_area': provider.service_area,
                'trusted_by': trusted_friends
            })
        
        return Response({
            'category': category.name,
            'city': city_filter,
            'providers_count': len(providers_data),
            'providers': providers_data
        })
        
    except ServiceCategory.DoesNotExist:
        return Response({'error': f'Service category "{category_name}" not found'}, status=404)

def generate_contact_reviews_for_provider(provider_id, user_id):
    """Generate consistent contact reviews for a provider-user combination"""
    import random
    
    seed_value = hash(f"{user_id}-{str(provider_id)}")
    random.seed(seed_value)
    
    fake_contacts = ['Harshita', 'Lakshit', 'Rohan', 'Priya']
    
    review_templates = [
        {'rating': 5, 'comment': 'Excellent service! Very professional and punctual.', 'is_trusted': True},
        {'rating': 4, 'comment': 'Good work, satisfied with the service.', 'is_trusted': True},
        {'rating': 3, 'comment': 'Average service, nothing special.', 'is_trusted': False},
        {'rating': 2, 'comment': 'Not good. Had to call them multiple times.', 'is_trusted': False},
        {'rating': 1, 'comment': 'Very disappointed. Poor quality work.', 'is_trusted': False},
        {'rating': 4, 'comment': 'Reliable and affordable. Would recommend.', 'is_trusted': True},
        {'rating': 5, 'comment': 'Best in the area! Very skilled and honest.', 'is_trusted': True},
        {'rating': 2, 'comment': 'Overpriced and slow service.', 'is_trusted': False},
    ]
    
    num_contact_reviews = random.randint(1, 3)
    contact_reviews = []
    
    if num_contact_reviews > 0:
        selected_contacts = random.sample(fake_contacts, num_contact_reviews)
        for contact_name in selected_contacts:
            review_template = random.choice(review_templates)
            contact_reviews.append({
                'user': contact_name,
                'rating': review_template['rating'],
                'comment': review_template['comment'],
                'is_trusted': review_template['is_trusted'],
            })
    
    random.seed()
    return contact_reviews


def get_trusted_friends(provider, request):
    """Get list of friends who trusted this provider - consistent with detail page"""
    
    # Auth check first
    if not request.user.is_authenticated:
        return {
            'count': 0,
            'message': 'No friends have used this service yet',
            'names': []
        }
    
    # Use user ID for consistent results
    user_id = request.user.id
    
    # Generate the same contact reviews as provider_detail will
    contact_reviews = generate_contact_reviews_for_provider(str(provider._id), user_id)
    
    # Filter only trusted contacts (those who recommended)
    trusted_contacts = [review['user'] for review in contact_reviews if review['is_trusted']]
    trusted_count = len(trusted_contacts)
    
    if trusted_count == 0:
        return {
            'count': 0,
            'message': 'No friends have used this service yet',
            'names': []
        }
    elif trusted_count == 1:
        return {
            'count': 1,
            'message': f'Trusted by {trusted_contacts[0]}',
            'names': [trusted_contacts[0]]
        }
    elif trusted_count == 2:
        return {
            'count': 2,
            'message': f'Trusted by {trusted_contacts[0]} and {trusted_contacts[1]}',
            'names': trusted_contacts
        }
    else:
        return {
            'count': trusted_count,
            'message': f'Trusted by {trusted_contacts[0]} and {trusted_count-1} others',
            'names': trusted_contacts
        }

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow both authenticated and non-authenticated
def provider_detail(request, provider_id):
    """Get detailed info about a specific provider with reviews"""
    import random
    
    try:
        object_id = ObjectId(provider_id)
        provider = get_object_or_404(ServiceProvider, _id=object_id)
    except (InvalidId, ValueError):
        return Response({'error': 'Invalid provider ID'}, status=400)
    
    db_reviews = Review.objects.filter(provider_id=provider_id).order_by('-created_at')
    
    actual_reviews = []
    for review in db_reviews:
        actual_reviews.append({
            'user': review.user.username,
            'is_contact': False,
            'rating': review.rating,
            'comment': review.comment,
            'is_trusted': review.is_trusted,
            'service_date': str(review.service_date) if review.service_date else None,
            'created_at': review.created_at.strftime('%B %d, %Y')
        })
    
    # Generate contact reviews ONLY if authenticated
    contact_reviews = []
    if request.user.is_authenticated:
        user_id = request.user.id
        # Use the helper function for consistency with list page
        contact_reviews_data = generate_contact_reviews_for_provider(str(provider._id), user_id)
        
        # Convert to frontend format
        for review_data in contact_reviews_data:
            contact_reviews.append({
                'user': review_data['user'],
                'is_contact': True,
                'rating': review_data['rating'],
                'comment': review_data['comment'],
                'is_trusted': review_data['is_trusted'],
                'service_date': None,
                'created_at': 'Recent'
            })
    
    # Generate other random reviews (always show these, even when logged out)
    random.seed(hash(f"other-{str(provider._id)}"))
    
    random_names = ['Amit K.', 'Sneha P.', 'Rajesh M.', 'Pooja S.', 'Vikram T.', 'Anita R.']
    other_reviews = []
    num_other_reviews = random.randint(2, 5)
    
    review_templates = [
        {'rating': 5, 'comment': 'Excellent service! Very professional and punctual.', 'is_trusted': True},
        {'rating': 4, 'comment': 'Good work, satisfied with the service.', 'is_trusted': True},
        {'rating': 3, 'comment': 'Average service, nothing special.', 'is_trusted': False},
        {'rating': 2, 'comment': 'Not good. Had to call them multiple times.', 'is_trusted': False},
        {'rating': 1, 'comment': 'Very disappointed. Poor quality work.', 'is_trusted': False},
        {'rating': 4, 'comment': 'Reliable and affordable. Would recommend.', 'is_trusted': True},
        {'rating': 5, 'comment': 'Best in the area! Very skilled and honest.', 'is_trusted': True},
        {'rating': 2, 'comment': 'Overpriced and slow service.', 'is_trusted': False},
    ]
    
    for _ in range(num_other_reviews):
        review_template = random.choice(review_templates)
        other_reviews.append({
            'user': random.choice(random_names),
            'is_contact': False,
            'rating': review_template['rating'],
            'comment': review_template['comment'],
            'is_trusted': review_template['is_trusted'],
            'service_date': None,
            'created_at': f'{random.randint(1, 30)} days ago'
        })
    
    random.seed()
    
    # Calculate trusted_by ONLY if authenticated
    if request.user.is_authenticated:
        trusted_contacts = [review for review in contact_reviews if review['is_trusted']]
        trusted_count = len(trusted_contacts)
        
        if trusted_count == 0:
            trusted_friends = {
                'count': 0,
                'message': 'No friends have used this service yet',
                'names': []
            }
        elif trusted_count == 1:
            trusted_friends = {
                'count': 1,
                'message': f'Trusted by {trusted_contacts[0]["user"]}',
                'names': [trusted_contacts[0]["user"]]
            }
        elif trusted_count == 2:
            trusted_friends = {
                'count': 2,
                'message': f'Trusted by {trusted_contacts[0]["user"]} and {trusted_contacts[1]["user"]}',
                'names': [c["user"] for c in trusted_contacts]
            }
        else:
            trusted_friends = {
                'count': trusted_count,
                'message': f'Trusted by {trusted_contacts[0]["user"]} and {trusted_count-1} others',
                'names': [c["user"] for c in trusted_contacts]
            }
    else:
        # Not authenticated - no trusted friends shown
        trusted_friends = {
            'count': 0,
            'message': 'No friends have used this service yet',
            'names': []
        }
    
    # Combine all reviews
    all_reviews_combined = actual_reviews + contact_reviews + other_reviews
    
    return Response({
        'provider': {
            'id': str(provider._id),
            'name': provider.name,
            'phone': provider.phone_number,
            'email': provider.email,
            'category': provider.category_name,
            'address': provider.address,
            'city': provider.city,  # ADD THIS LINE
            'service_area': provider.service_area,
            'experience_years': provider.experience_years,
            'rating': provider.rating,
            'total_reviews': provider.total_reviews,
        },
        'trusted_by': trusted_friends,
        'recent_reviews': all_reviews_combined,
        'reviews': {
            'from_contacts': contact_reviews,
            'from_others': other_reviews + actual_reviews,
            'total': len(all_reviews_combined)
        }
    })


# Booking Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    """Create a new booking"""
    serializer = BookingSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create booking without saving
        booking = Booking(
            provider_id=serializer.validated_data['provider_id'],
            booking_date=serializer.validated_data['booking_date'],
            booking_time=serializer.validated_data['booking_time'],
            notes=serializer.validated_data.get('notes', ''),
            status='pending'
        )
        booking.user_id = request.user.id
        booking.save()  # Save only once
        
        return Response({
            'message': 'Booking created successfully!',
            'booking': BookingSerializer(booking).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_bookings(request):
    """Get all bookings for current user"""
    bookings_list = list(Booking.objects.filter(user_id=request.user.id))  # CHANGED
    serializer = BookingSerializer(bookings_list, many=True)
    
    return Response({
        'count': len(bookings_list),
        'bookings': serializer.data
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    try:
        from bson import ObjectId
        from bson.errors import InvalidId
        object_id = ObjectId(booking_id)
        booking = Booking.objects.get(_id=object_id, user_id=request.user.id)  # CHANGED
        booking.status = 'cancelled'
        booking.save()
        
        serializer = BookingSerializer(booking)
        return Response({
            'message': 'Booking cancelled successfully!',
            'booking': serializer.data
        })
    except (InvalidId, ValueError):
        return Response({'error': 'Invalid booking ID'}, status=status.HTTP_400_BAD_REQUEST)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request, provider_id):
    """Submit a review for a service provider"""
    try:
        object_id = ObjectId(provider_id)
        provider = ServiceProvider.objects.get(_id=object_id)
    except (InvalidId, ValueError):
        return Response({'error': 'Invalid provider ID'}, status=status.HTTP_400_BAD_REQUEST)
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # CHANGED: Check if user already reviewed - use user_id
    existing_reviews = list(Review.objects.filter(user_id=request.user.id, provider_id=str(provider_id)))
    existing_review = existing_reviews[0] if existing_reviews else None
    
    rating = request.data.get('rating')
    comment = request.data.get('comment', '')
    is_trusted = request.data.get('is_trusted', False)
    
    if not rating or int(rating) < 1 or int(rating) > 5:
        return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
    
    if existing_review:
        existing_review.rating = int(rating)
        existing_review.comment = comment
        existing_review.is_trusted = is_trusted
        existing_review.save()
        message = 'Review updated successfully!'
    else:
        # CHANGED: Create with user_id
        review = Review(
            provider_id=str(provider_id),
            rating=int(rating),
            comment=comment,
            is_trusted=is_trusted
        )
        review.user_id = request.user.id
        review.save()
        message = 'Review submitted successfully!'
    
    # Calculate weighted average - use list()
    real_reviews_list = list(Review.objects.filter(provider_id=str(provider_id)))
    fake_count = 10
    fake_rating = provider.original_rating
    
    if len(real_reviews_list) > 0:
        avg_real = sum(r.rating for r in real_reviews_list) / len(real_reviews_list)
        real_count = len(real_reviews_list)
        
        provider.rating = round(
            (fake_rating * fake_count + avg_real * real_count) / (fake_count + real_count), 
            1
        )
        provider.total_reviews = fake_count + real_count
    else:
        provider.total_reviews = fake_count
    
    provider.save()
    
    return Response({
        'message': message,
        'provider': {
            'id': str(provider._id),
            'name': provider.name,
            'rating': provider.rating,
            'total_reviews': provider.total_reviews
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def provider_register(request):
    """Register as a service provider"""
    serializer = ProviderRegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        # CHANGED: Get provider using user_id instead of user
        try:
            provider = ServiceProvider.objects.get(user_id=user.id)
        except ServiceProvider.DoesNotExist:
            provider = None
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': 'provider'
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Provider registered successfully!'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_dashboard(request):
    """Get provider dashboard statistics"""
    try:
        from datetime import datetime, timedelta
        provider = ServiceProvider.objects.get(user_id=request.user.id)  # CHANGED
        
        # Get all bookings for this provider
        all_bookings = list(Booking.objects.filter(provider_id=str(provider._id)))
        
        # Calculate statistics
        today = datetime.now().date()
        
        today_bookings = [b for b in all_bookings if b.booking_date == today]
        week_start = today - timedelta(days=today.weekday())
        week_bookings = [b for b in all_bookings if b.booking_date >= week_start]
        month_bookings = [b for b in all_bookings if b.booking_date.month == today.month]
        
        pending_count = len([b for b in all_bookings if b.status == 'pending'])
        
        return Response({
            'provider': ServiceProviderSerializer(provider).data,
            'statistics': {
                'total_bookings': len(all_bookings),
                'today_bookings': len(today_bookings),
                'week_bookings': len(week_bookings),
                'month_bookings': len(month_bookings),
                'pending_requests': pending_count,
                'average_rating': provider.rating,
                'total_reviews': provider.total_reviews,
            }
        })
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_bookings(request):
    """Get all bookings for the provider"""
    try:
        provider = ServiceProvider.objects.get(user_id=request.user.id)  # CHANGED
        bookings = list(Booking.objects.filter(provider_id=str(provider._id)))
        
        # Group by status
        pending = [b for b in bookings if b.status == 'pending']
        accepted = [b for b in bookings if b.status == 'accepted']
        completed = [b for b in bookings if b.status == 'completed']
        cancelled = [b for b in bookings if b.status in ['cancelled', 'rejected']]
        
        return Response({
            'all': ProviderBookingSerializer(bookings, many=True).data,
            'pending': ProviderBookingSerializer(pending, many=True).data,
            'accepted': ProviderBookingSerializer(accepted, many=True).data,
            'completed': ProviderBookingSerializer(completed, many=True).data,
            'cancelled': ProviderBookingSerializer(cancelled, many=True).data,
        })
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def provider_accept_booking(request, booking_id):
    """Accept a booking request"""
    try:
        provider = ServiceProvider.objects.get(user_id=request.user.id)  # CHANGED
        booking = Booking.objects.get(_id=ObjectId(booking_id), provider_id=str(provider._id))
        
        if booking.status != 'pending':
            return Response({'error': 'Booking is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'accepted'
        booking.provider_status = 'accepted'
        booking.save()
        
        return Response({
            'message': 'Booking accepted successfully!',
            'booking': ProviderBookingSerializer(booking).data
        })
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def provider_reject_booking(request, booking_id):
    """Reject a booking request"""
    try:
        provider = ServiceProvider.objects.get(user_id=request.user.id)  # CHANGED
        booking = Booking.objects.get(_id=ObjectId(booking_id), provider_id=str(provider._id))
        
        if booking.status != 'pending':
            return Response({'error': 'Booking is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'rejected'
        booking.provider_status = 'rejected'
        booking.save()
        
        return Response({
            'message': 'Booking rejected',
            'booking': ProviderBookingSerializer(booking).data
        })
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def provider_complete_booking(request, booking_id):
    """Mark booking as completed"""
    try:
        from datetime import datetime
        
        provider = ServiceProvider.objects.get(user_id=request.user.id)  # CHANGED
        booking = Booking.objects.get(_id=ObjectId(booking_id), provider_id=str(provider._id))
        
        if booking.status not in ['pending', 'accepted']:
            return Response({'error': 'Booking cannot be marked as completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'completed'
        booking.provider_status = 'completed'
        booking.completion_notes = request.data.get('completion_notes', '')
        booking.completed_at = datetime.now()
        booking.save()
        
        return Response({
            'message': 'Booking marked as completed!',
            'booking': ProviderBookingSerializer(booking).data
        })
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_reviews(request):
    """Get all reviews for the provider"""
    try:
        provider = ServiceProvider.objects.get(user_id=request.user.id)  # CHANGED
        reviews = list(Review.objects.filter(provider_id=str(provider._id)))
        
        # Group by rating
        reviews_by_rating = {
            5: len([r for r in reviews if r.rating == 5]),
            4: len([r for r in reviews if r.rating == 4]),
            3: len([r for r in reviews if r.rating == 3]),
            2: len([r for r in reviews if r.rating == 2]),
            1: len([r for r in reviews if r.rating == 1]),
        }
        
        reviews_data = []
        for r in reviews:
            # Get username from user_id
            try:
                user = User.objects.get(id=r.user_id)
                username = user.username
            except:
                username = "Unknown"
            
            reviews_data.append({
                'id': r.id,
                'customer': username,
                'rating': r.rating,
                'comment': r.comment,
                'is_trusted': r.is_trusted,
                'created_at': r.created_at.strftime('%B %d, %Y'),
            })
        
        return Response({
            'total_reviews': len(reviews),
            'average_rating': provider.rating,
            'rating_breakdown': reviews_by_rating,
            'reviews': reviews_data
        })
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def provider_profile(request):
    """Get or update provider profile"""
    try:
        provider = ServiceProvider.objects.get(user_id=request.user.id)  # CHANGED
        
        if request.method == 'GET':
            return Response(ServiceProviderSerializer(provider).data)
        
        elif request.method == 'PUT':
            # Update allowed fields
            provider.name = request.data.get('name', provider.name)
            provider.phone_number = request.data.get('phone_number', provider.phone_number)
            provider.email = request.data.get('email', provider.email)
            provider.description = request.data.get('description', provider.description)
            provider.availability = request.data.get('availability', provider.availability)
            provider.service_area = request.data.get('service_area', provider.service_area)
            provider.address = request.data.get('address', provider.address)
            provider.save()
            
            return Response({
                'message': 'Profile updated successfully!',
                'provider': ServiceProviderSerializer(provider).data
            })
    except ServiceProvider.DoesNotExist:
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_404_NOT_FOUND)


def populate_fake_data(request):
    """Populate database with fake data for testing"""
    
    # Clear existing data
    ServiceProvider.objects.all().delete()
    ServiceCategory.objects.all().delete()
    
    categories_data = [
        {'name': 'Plumber', 'description': 'Expert plumbing services for leaks, installations, and repairs.'},
        {'name': 'Barber', 'description': 'Professional hairstyling and grooming services at your convenience.'},
        {'name': 'Carpenter', 'description': 'Skilled carpenters for furniture, repairs, and custom projects.'},
        {'name': 'Electrician', 'description': 'Certified electricians for installations, repairs, and maintenance.'},
        {'name': 'AC Service', 'description': 'Professional AC maintenance, servicing, and repair solutions.'},
        {'name': 'Appliance Repair', 'description': 'Expert repair services for all your home appliances.'}
    ]
    
    # Create categories
    for cat_data in categories_data:
        ServiceCategory.objects.create(
            name=cat_data['name'],
            description=cat_data['description'],
            icon=''
        )
    
    providers_data = [
        # Plumbers (7 providers)
        {'name': 'Raj Kumar', 'phone': '+91-9876543210', 'category': 'Plumber', 'rating': 4.5, 'experience': 5, 'address': 'Sector 22, Patiala', 'city': 'Patiala'},
        {'name': 'Suresh Singh', 'phone': '+91-9876543211', 'category': 'Plumber', 'rating': 4.2, 'experience': 3, 'address': 'Urban Estate, Patiala', 'city': 'Patiala'},
        {'name': 'Amit Plumbing Services', 'phone': '+91-9876543216', 'category': 'Plumber', 'rating': 4.7, 'experience': 8, 'address': 'Model Town, Patiala', 'city': 'Patiala'},
        {'name': 'Quick Fix Plumbers', 'phone': '+91-9876543217', 'category': 'Plumber', 'rating': 4.3, 'experience': 4, 'address': 'Rajpura Road, Patiala', 'city': 'Patiala'},
        {'name': 'Expert Plumbing Co.', 'phone': '+91-9876543218', 'category': 'Plumber', 'rating': 4.6, 'experience': 6, 'address': 'Tripuri Town, Patiala', 'city': 'Patiala'},
        {'name': 'Singh Plumbing Works', 'phone': '+91-9876543219', 'category': 'Plumber', 'rating': 4.4, 'experience': 7, 'address': 'Leela Bhawan, Patiala', 'city': 'Patiala'},
        {'name': 'Modern Plumbers', 'phone': '+91-9876543220', 'category': 'Plumber', 'rating': 4.8, 'experience': 10, 'address': 'Mall Road, Patiala', 'city': 'Patiala'},
        
        # Barbers (7 providers)
        {'name': 'Hair Studio - Amit', 'phone': '+91-9876543212', 'category': 'Barber', 'rating': 4.8, 'experience': 7, 'address': 'Mall Road, Patiala', 'city': 'Patiala'},
        {'name': 'Style Cut - Rohit', 'phone': '+91-9876543213', 'category': 'Barber', 'rating': 4.3, 'experience': 4, 'address': 'Leela Bhawan, Patiala', 'city': 'Patiala'},
        {'name': 'Gents Salon - Rakesh', 'phone': '+91-9876543221', 'category': 'Barber', 'rating': 4.5, 'experience': 5, 'address': 'Sector 22, Patiala', 'city': 'Patiala'},
        {'name': 'Royal Cuts', 'phone': '+91-9876543222', 'category': 'Barber', 'rating': 4.6, 'experience': 6, 'address': 'Urban Estate, Patiala', 'city': 'Patiala'},
        {'name': 'Modern Hair Studio', 'phone': '+91-9876543223', 'category': 'Barber', 'rating': 4.7, 'experience': 8, 'address': 'Model Town, Patiala', 'city': 'Patiala'},
        {'name': 'Trim & Style Salon', 'phone': '+91-9876543224', 'category': 'Barber', 'rating': 4.4, 'experience': 3, 'address': 'Rajpura Road, Patiala', 'city': 'Patiala'},
        {'name': 'Elite Barber Shop', 'phone': '+91-9876543225', 'category': 'Barber', 'rating': 4.9, 'experience': 12, 'address': 'Tripuri Town, Patiala', 'city': 'Patiala'},
        
        # Carpenters (7 providers)
        {'name': 'Wood Works - Ramesh', 'phone': '+91-9876543214', 'category': 'Carpenter', 'rating': 4.6, 'experience': 8, 'address': 'Bahadurgarh Road, Patiala', 'city': 'Patiala'},
        {'name': 'Master Carpenter - Vijay', 'phone': '+91-9876543226', 'category': 'Carpenter', 'rating': 4.5, 'experience': 6, 'address': 'Sector 22, Patiala', 'city': 'Patiala'},
        {'name': 'Furniture Experts', 'phone': '+91-9876543227', 'category': 'Carpenter', 'rating': 4.7, 'experience': 9, 'address': 'Mall Road, Patiala', 'city': 'Patiala'},
        {'name': 'Custom Wood Works', 'phone': '+91-9876543228', 'category': 'Carpenter', 'rating': 4.4, 'experience': 5, 'address': 'Urban Estate, Patiala', 'city': 'Patiala'},
        {'name': 'Singh Carpentry', 'phone': '+91-9876543229', 'category': 'Carpenter', 'rating': 4.8, 'experience': 10, 'address': 'Model Town, Patiala', 'city': 'Patiala'},
        {'name': 'Precision Carpenters', 'phone': '+91-9876543230', 'category': 'Carpenter', 'rating': 4.3, 'experience': 4, 'address': 'Leela Bhawan, Patiala', 'city': 'Patiala'},
        {'name': 'Elite Furniture Makers', 'phone': '+91-9876543231', 'category': 'Carpenter', 'rating': 4.9, 'experience': 15, 'address': 'Tripuri Town, Patiala', 'city': 'Patiala'},
        
        # Electricians (7 providers)
        {'name': 'Power Solutions - Ankit', 'phone': '+91-9876543232', 'category': 'Electrician', 'rating': 4.6, 'experience': 7, 'address': 'Sector 22, Patiala', 'city': 'Patiala'},
        {'name': 'Safe Electric Works', 'phone': '+91-9876543233', 'category': 'Electrician', 'rating': 4.4, 'experience': 5, 'address': 'Mall Road, Patiala', 'city': 'Patiala'},
        {'name': 'Quick Fix Electricians', 'phone': '+91-9876543234', 'category': 'Electrician', 'rating': 4.7, 'experience': 8, 'address': 'Urban Estate, Patiala', 'city': 'Patiala'},
        {'name': 'Expert Electrical Services', 'phone': '+91-9876543235', 'category': 'Electrician', 'rating': 4.5, 'experience': 6, 'address': 'Model Town, Patiala', 'city': 'Patiala'},
        {'name': 'Modern Electricians', 'phone': '+91-9876543236', 'category': 'Electrician', 'rating': 4.8, 'experience': 10, 'address': 'Rajpura Road, Patiala', 'city': 'Patiala'},
        {'name': 'Reliable Electric Co.', 'phone': '+91-9876543237', 'category': 'Electrician', 'rating': 4.3, 'experience': 4, 'address': 'Leela Bhawan, Patiala', 'city': 'Patiala'},
        {'name': 'Lightning Electric Works', 'phone': '+91-9876543238', 'category': 'Electrician', 'rating': 4.9, 'experience': 12, 'address': 'Tripuri Town, Patiala', 'city': 'Patiala'},
        
        # AC Service (7 providers)
        {'name': 'AC Master - Vikram', 'phone': '+91-9876543215', 'category': 'AC Service', 'rating': 4.4, 'experience': 6, 'address': 'Sirhind Road, Patiala', 'city': 'Patiala'},
        {'name': 'Cool Care AC Services', 'phone': '+91-9876543239', 'category': 'AC Service', 'rating': 4.6, 'experience': 7, 'address': 'Sector 22, Patiala', 'city': 'Patiala'},
        {'name': 'Expert AC Repair', 'phone': '+91-9876543240', 'category': 'AC Service', 'rating': 4.5, 'experience': 5, 'address': 'Mall Road, Patiala', 'city': 'Patiala'},
        {'name': 'Quick Cool Services', 'phone': '+91-9876543241', 'category': 'AC Service', 'rating': 4.7, 'experience': 8, 'address': 'Urban Estate, Patiala', 'city': 'Patiala'},
        {'name': 'Arctic AC Solutions', 'phone': '+91-9876543242', 'category': 'AC Service', 'rating': 4.8, 'experience': 9, 'address': 'Model Town, Patiala', 'city': 'Patiala'},
        {'name': 'Chill Point AC Repair', 'phone': '+91-9876543243', 'category': 'AC Service', 'rating': 4.3, 'experience': 4, 'address': 'Rajpura Road, Patiala', 'city': 'Patiala'},
        {'name': 'Pro AC Technicians', 'phone': '+91-9876543244', 'category': 'AC Service', 'rating': 4.9, 'experience': 11, 'address': 'Tripuri Town, Patiala', 'city': 'Patiala'},
        
        # Appliance Repair (7 providers)
        {'name': 'Home Appliance Experts', 'phone': '+91-9876543245', 'category': 'Appliance Repair', 'rating': 4.5, 'experience': 6, 'address': 'Sector 22, Patiala', 'city': 'Patiala'},
        {'name': 'Fix All Appliances', 'phone': '+91-9876543246', 'category': 'Appliance Repair', 'rating': 4.4, 'experience': 5, 'address': 'Mall Road, Patiala', 'city': 'Patiala'},
        {'name': 'Smart Repair Services', 'phone': '+91-9876543247', 'category': 'Appliance Repair', 'rating': 4.7, 'experience': 8, 'address': 'Urban Estate, Patiala', 'city': 'Patiala'},
        {'name': 'Quick Fix Appliances', 'phone': '+91-9876543248', 'category': 'Appliance Repair', 'rating': 4.6, 'experience': 7, 'address': 'Model Town, Patiala', 'city': 'Patiala'},
        {'name': 'Modern Appliance Care', 'phone': '+91-9876543249', 'category': 'Appliance Repair', 'rating': 4.8, 'experience': 9, 'address': 'Rajpura Road, Patiala', 'city': 'Patiala'},
        {'name': 'Expert Appliance Solutions', 'phone': '+91-9876543250', 'category': 'Appliance Repair', 'rating': 4.3, 'experience': 4, 'address': 'Leela Bhawan, Patiala', 'city': 'Patiala'},
        {'name': 'Reliable Repairs Hub', 'phone': '+91-9876543251', 'category': 'Appliance Repair', 'rating': 4.9, 'experience': 10, 'address': 'Tripuri Town, Patiala', 'city': 'Patiala'},
    ]
    
    # Create providers
    created = 0
    for prov in providers_data:
        ServiceProvider.objects.create(
            name=prov['name'],
            phone_number=prov['phone'],
            category_name=prov['category'],
            rating=prov['rating'],
            original_rating=prov['rating'],
            experience_years=prov['experience'],
            total_reviews=10,
            address=prov['address'],
            city=prov.get('city', 'Patiala'),
            email=''
        )
        created += 1
    
    return JsonResponse({
        'message': 'Fake data populated successfully!',
        'categories': ServiceCategory.objects.count(),
        'providers': created
    })