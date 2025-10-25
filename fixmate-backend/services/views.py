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
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer, BookingSerializer

# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
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
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
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
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

# Service Views
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

def service_providers(request, category_name):
    """Show providers for a specific service category with social proof"""
    try:
        category = ServiceCategory.objects.get(name__iexact=category_name)
        providers = ServiceProvider.objects.filter(category_name=category_name)
        
        providers_data = []
        for provider in providers:
            trusted_friends = get_trusted_friends(provider, request)
            
            providers_data.append({
                'id': str(provider._id),  # Use _id directly
                'name': provider.name,
                'phone': provider.phone_number,
                'email': provider.email,
                'rating': provider.rating,
                'total_reviews': provider.total_reviews,
                'experience_years': provider.experience_years,
                'address': provider.address,
                'trusted_by': trusted_friends
            })
        
        return JsonResponse({
            'category': category.name,
            'providers_count': len(providers_data),
            'providers': providers_data
        })
        
    except ServiceCategory.DoesNotExist:
        return JsonResponse({'error': f'Service category "{category_name}" not found'}, status=404)

def get_trusted_friends(provider, request):
    """Get list of friends who trusted this provider - randomized per provider"""
    import random
    
    if not request.user.is_authenticated:
        return {
            'count': 0,
            'message': 'No friends have used this service yet',
            'names': []
        }
    # Set seed based on provider ID for consistency
    random.seed(hash(provider.name))
    
    fake_contacts = [
        {'name': 'Harshita', 'phone': '+91-9876543220'},
        {'name': 'Lakshit', 'phone': '+91-9876543221'},
        {'name': 'Rohan', 'phone': '+91-9876543222'},
        {'name': 'Priya', 'phone': '+91-9876543223'},
    ]
    
    num_trusted = random.randint(0, len(fake_contacts))
    trusted_friends = random.sample(fake_contacts, num_trusted) if num_trusted > 0 else []
    trusted_count = len(trusted_friends)
    
    random.seed()
    
    if trusted_count == 0:
        return {
            'count': 0,
            'message': 'No friends have used this service yet',
            'names': []
        }
    elif trusted_count == 1:
        return {
            'count': 1,
            'message': f'Trusted by {trusted_friends[0]["name"]}',
            'names': [trusted_friends[0]["name"]]
        }
    elif trusted_count == 2:
        return {
            'count': 2,
            'message': f'Trusted by {trusted_friends[0]["name"]} and {trusted_friends[1]["name"]}',
            'names': [friend["name"] for friend in trusted_friends]
        }
    else:
        return {
            'count': trusted_count,
            'message': f'Trusted by {trusted_friends[0]["name"]} and {trusted_count-1} others',
            'names': [friend["name"] for friend in trusted_friends]
        }

def provider_detail(request, provider_id):
    """Get detailed info about a specific provider with reviews"""
    import random
    
    try:
        object_id = ObjectId(provider_id)
        provider = get_object_or_404(ServiceProvider, _id=object_id)
    except (InvalidId, ValueError):
        return JsonResponse({'error': 'Invalid provider ID'}, status=400)
    
    # Get actual reviews from database
    db_reviews = Review.objects.filter(provider_id=provider_id).order_by('-created_at')
    
    # Convert DB reviews to list
    actual_reviews = []
    for review in db_reviews:
        actual_reviews.append({
            'user': review.user.username,
            'is_contact': False,  # You can enhance this later with actual contacts
            'rating': review.rating,
            'comment': review.comment,
            'is_trusted': review.is_trusted,
            'service_date': str(review.service_date) if review.service_date else None,
            'created_at': review.created_at.strftime('%B %d, %Y')
        })
    
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
    # Check if user is authenticated before showing contact reviews
    contact_reviews = []
    if request.user.is_authenticated:
        fake_contacts = ['Harshita', 'Lakshit', 'Rohan', 'Priya']
        random.seed(hash(str(provider._id)))
        
        num_contact_reviews = random.randint(0, 3)
        
    
        if num_contact_reviews > 0:
            selected_contacts = random.sample(fake_contacts, num_contact_reviews)
            for contact_name in selected_contacts:
                review_template = random.choice(review_templates)
                contact_reviews.append({
                    'user': contact_name,
                    'is_contact': True,
                    'rating': review_template['rating'],
                    'comment': review_template['comment'],
                    'is_trusted': review_template['is_trusted'],
                    'service_date': None,
                    'created_at': 'Recent'
                })

    random_names = ['Amit K.', 'Sneha P.', 'Rajesh M.', 'Pooja S.', 'Vikram T.', 'Anita R.']
    other_reviews = []
    num_other_reviews = random.randint(2, 5)
    
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
    
    # Combine all reviews: actual reviews + fake contact reviews + fake other reviews
    all_reviews_combined = actual_reviews + contact_reviews + other_reviews
    
    trusted_friends = get_trusted_friends(provider, request)
    
    return JsonResponse({
        'provider': {
            'id': str(provider._id),
            'name': provider.name,
            'phone': provider.phone_number,
            'email': provider.email,
            'category': provider.category_name,
            'address': provider.address,
            'experience_years': provider.experience_years,
            'rating': provider.rating,
            'total_reviews': provider.total_reviews,
        },
        'trusted_by': trusted_friends,
        'recent_reviews': all_reviews_combined,  # Add this field that frontend expects
        'reviews': {
            'from_contacts': contact_reviews,
            'from_others': other_reviews + actual_reviews,  # Include actual reviews here
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
        serializer.save(user=request.user)
        return Response({
            'message': 'Booking created successfully!',
            'booking': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_bookings(request):
    """Get all bookings for current user"""
    bookings_list = list(Booking.objects.filter(user=request.user))  # FIXED: Use list()
    serializer = BookingSerializer(bookings_list, many=True)
    
    return Response({
        'count': len(bookings_list),  # FIXED: Use len() instead of .count()
        'bookings': serializer.data
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    try:
        # Convert string booking_id to ObjectId
        from bson import ObjectId
        from bson.errors import InvalidId
        object_id = ObjectId(booking_id)
        booking = Booking.objects.get(_id=object_id, user=request.user)
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
    
    # Check if user already reviewed - use list() instead of .exists()
    existing_reviews = list(Review.objects.filter(user=request.user, provider_id=str(provider_id)))
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
        Review.objects.create(
            user=request.user,
            provider_id=str(provider_id),
            rating=int(rating),
            comment=comment,
            is_trusted=is_trusted
        )
        message = 'Review submitted successfully!'
    
    # Calculate weighted average - use list() instead of queryset methods
    real_reviews_list = list(Review.objects.filter(provider_id=str(provider_id)))
    fake_count = 10
    fake_rating = provider.original_rating
    
    if len(real_reviews_list) > 0:  # Changed from .exists()
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
        {'name': 'Raj Kumar', 'phone': '+91-9876543210', 'category': 'Plumber', 'rating': 4.5, 'experience': 5, 'address': 'Sector 22, Patiala'},
        {'name': 'Suresh Singh', 'phone': '+91-9876543211', 'category': 'Plumber', 'rating': 4.2, 'experience': 3, 'address': 'Urban Estate, Patiala'},
        {'name': 'Amit Plumbing Services', 'phone': '+91-9876543216', 'category': 'Plumber', 'rating': 4.7, 'experience': 8, 'address': 'Model Town, Patiala'},
        {'name': 'Quick Fix Plumbers', 'phone': '+91-9876543217', 'category': 'Plumber', 'rating': 4.3, 'experience': 4, 'address': 'Rajpura Road, Patiala'},
        {'name': 'Expert Plumbing Co.', 'phone': '+91-9876543218', 'category': 'Plumber', 'rating': 4.6, 'experience': 6, 'address': 'Tripuri Town, Patiala'},
        {'name': 'Singh Plumbing Works', 'phone': '+91-9876543219', 'category': 'Plumber', 'rating': 4.4, 'experience': 7, 'address': 'Leela Bhawan, Patiala'},
        {'name': 'Modern Plumbers', 'phone': '+91-9876543220', 'category': 'Plumber', 'rating': 4.8, 'experience': 10, 'address': 'Mall Road, Patiala'},
        
        # Barbers (7 providers)
        {'name': 'Hair Studio - Amit', 'phone': '+91-9876543212', 'category': 'Barber', 'rating': 4.8, 'experience': 7, 'address': 'Mall Road, Patiala'},
        {'name': 'Style Cut - Rohit', 'phone': '+91-9876543213', 'category': 'Barber', 'rating': 4.3, 'experience': 4, 'address': 'Leela Bhawan, Patiala'},
        {'name': 'Gents Salon - Rakesh', 'phone': '+91-9876543221', 'category': 'Barber', 'rating': 4.5, 'experience': 5, 'address': 'Sector 22, Patiala'},
        {'name': 'Royal Cuts', 'phone': '+91-9876543222', 'category': 'Barber', 'rating': 4.6, 'experience': 6, 'address': 'Urban Estate, Patiala'},
        {'name': 'Modern Hair Studio', 'phone': '+91-9876543223', 'category': 'Barber', 'rating': 4.7, 'experience': 8, 'address': 'Model Town, Patiala'},
        {'name': 'Trim & Style Salon', 'phone': '+91-9876543224', 'category': 'Barber', 'rating': 4.4, 'experience': 3, 'address': 'Rajpura Road, Patiala'},
        {'name': 'Elite Barber Shop', 'phone': '+91-9876543225', 'category': 'Barber', 'rating': 4.9, 'experience': 12, 'address': 'Tripuri Town, Patiala'},
        
        # Carpenters (7 providers)
        {'name': 'Wood Works - Ramesh', 'phone': '+91-9876543214', 'category': 'Carpenter', 'rating': 4.6, 'experience': 8, 'address': 'Bahadurgarh Road, Patiala'},
        {'name': 'Master Carpenter - Vijay', 'phone': '+91-9876543226', 'category': 'Carpenter', 'rating': 4.5, 'experience': 6, 'address': 'Sector 22, Patiala'},
        {'name': 'Furniture Experts', 'phone': '+91-9876543227', 'category': 'Carpenter', 'rating': 4.7, 'experience': 9, 'address': 'Mall Road, Patiala'},
        {'name': 'Custom Wood Works', 'phone': '+91-9876543228', 'category': 'Carpenter', 'rating': 4.4, 'experience': 5, 'address': 'Urban Estate, Patiala'},
        {'name': 'Singh Carpentry', 'phone': '+91-9876543229', 'category': 'Carpenter', 'rating': 4.8, 'experience': 10, 'address': 'Model Town, Patiala'},
        {'name': 'Precision Carpenters', 'phone': '+91-9876543230', 'category': 'Carpenter', 'rating': 4.3, 'experience': 4, 'address': 'Leela Bhawan, Patiala'},
        {'name': 'Elite Furniture Makers', 'phone': '+91-9876543231', 'category': 'Carpenter', 'rating': 4.9, 'experience': 15, 'address': 'Tripuri Town, Patiala'},
        
        # Electricians (7 providers)
        {'name': 'Power Solutions - Ankit', 'phone': '+91-9876543232', 'category': 'Electrician', 'rating': 4.6, 'experience': 7, 'address': 'Sector 22, Patiala'},
        {'name': 'Safe Electric Works', 'phone': '+91-9876543233', 'category': 'Electrician', 'rating': 4.4, 'experience': 5, 'address': 'Mall Road, Patiala'},
        {'name': 'Quick Fix Electricians', 'phone': '+91-9876543234', 'category': 'Electrician', 'rating': 4.7, 'experience': 8, 'address': 'Urban Estate, Patiala'},
        {'name': 'Expert Electrical Services', 'phone': '+91-9876543235', 'category': 'Electrician', 'rating': 4.5, 'experience': 6, 'address': 'Model Town, Patiala'},
        {'name': 'Modern Electricians', 'phone': '+91-9876543236', 'category': 'Electrician', 'rating': 4.8, 'experience': 10, 'address': 'Rajpura Road, Patiala'},
        {'name': 'Reliable Electric Co.', 'phone': '+91-9876543237', 'category': 'Electrician', 'rating': 4.3, 'experience': 4, 'address': 'Leela Bhawan, Patiala'},
        {'name': 'Lightning Electric Works', 'phone': '+91-9876543238', 'category': 'Electrician', 'rating': 4.9, 'experience': 12, 'address': 'Tripuri Town, Patiala'},
        
        # AC Service (7 providers)
        {'name': 'AC Master - Vikram', 'phone': '+91-9876543215', 'category': 'AC Service', 'rating': 4.4, 'experience': 6, 'address': 'Sirhind Road, Patiala'},
        {'name': 'Cool Care AC Services', 'phone': '+91-9876543239', 'category': 'AC Service', 'rating': 4.6, 'experience': 7, 'address': 'Sector 22, Patiala'},
        {'name': 'Expert AC Repair', 'phone': '+91-9876543240', 'category': 'AC Service', 'rating': 4.5, 'experience': 5, 'address': 'Mall Road, Patiala'},
        {'name': 'Quick Cool Services', 'phone': '+91-9876543241', 'category': 'AC Service', 'rating': 4.7, 'experience': 8, 'address': 'Urban Estate, Patiala'},
        {'name': 'Arctic AC Solutions', 'phone': '+91-9876543242', 'category': 'AC Service', 'rating': 4.8, 'experience': 9, 'address': 'Model Town, Patiala'},
        {'name': 'Chill Point AC Repair', 'phone': '+91-9876543243', 'category': 'AC Service', 'rating': 4.3, 'experience': 4, 'address': 'Rajpura Road, Patiala'},
        {'name': 'Pro AC Technicians', 'phone': '+91-9876543244', 'category': 'AC Service', 'rating': 4.9, 'experience': 11, 'address': 'Tripuri Town, Patiala'},
        
        # Appliance Repair (7 providers)
        {'name': 'Home Appliance Experts', 'phone': '+91-9876543245', 'category': 'Appliance Repair', 'rating': 4.5, 'experience': 6, 'address': 'Sector 22, Patiala'},
        {'name': 'Fix All Appliances', 'phone': '+91-9876543246', 'category': 'Appliance Repair', 'rating': 4.4, 'experience': 5, 'address': 'Mall Road, Patiala'},
        {'name': 'Smart Repair Services', 'phone': '+91-9876543247', 'category': 'Appliance Repair', 'rating': 4.7, 'experience': 8, 'address': 'Urban Estate, Patiala'},
        {'name': 'Quick Fix Appliances', 'phone': '+91-9876543248', 'category': 'Appliance Repair', 'rating': 4.6, 'experience': 7, 'address': 'Model Town, Patiala'},
        {'name': 'Modern Appliance Care', 'phone': '+91-9876543249', 'category': 'Appliance Repair', 'rating': 4.8, 'experience': 9, 'address': 'Rajpura Road, Patiala'},
        {'name': 'Expert Appliance Solutions', 'phone': '+91-9876543250', 'category': 'Appliance Repair', 'rating': 4.3, 'experience': 4, 'address': 'Leela Bhawan, Patiala'},
        {'name': 'Reliable Repairs Hub', 'phone': '+91-9876543251', 'category': 'Appliance Repair', 'rating': 4.9, 'experience': 10, 'address': 'Tripuri Town, Patiala'},
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
            email=''
        )
        created += 1
    
    return JsonResponse({
        'message': 'Fake data populated successfully!',
        'categories': ServiceCategory.objects.count(),
        'providers': created
    })