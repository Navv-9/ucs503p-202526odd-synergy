# services/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import ServiceCategory, ServiceProvider, Review, UserProfile, Contact

def home(request):
    """Homepage showing service categories"""
    categories = ServiceCategory.objects.all()
    return JsonResponse({
        'message': 'FixMate API - Service Categories',
        'categories': [
            {
                'id': cat.id,
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
        providers = ServiceProvider.objects.filter(category=category)
        
        providers_data = []
        for provider in providers:
            # Get social proof (trusted friends)
            trusted_friends = get_trusted_friends(provider, request)
            
            providers_data.append({
                'id': provider.id,
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
    """
    Get list of friends who trusted this provider
    For prototype: using fake data, later will use real contact sync
    """
    # Fake data for prototype - simulating "Trusted by Harshita and 2 others"
    fake_contacts = [
        {'name': 'Harshita', 'phone': '+91-9876543220', 'trusted': True},
        {'name': 'Lakshit', 'phone': '+91-9876543221', 'trusted': True},
        {'name': 'Rohan', 'phone': '+91-9876543222', 'trusted': False},
        {'name': 'Priya', 'phone': '+91-9876543223', 'trusted': True},
    ]
    
    # Filter trusted friends
    trusted_friends = [friend for friend in fake_contacts if friend['trusted']]
    trusted_count = len(trusted_friends)
    
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
    """Get detailed info about a specific provider"""
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    
    # Get recent reviews
    recent_reviews = Review.objects.filter(provider=provider).order_by('-created_at')[:5]
    
    # Get social proof
    trusted_friends = get_trusted_friends(provider, request)
    
    reviews_data = []
    for review in recent_reviews:
        reviews_data.append({
            'user': review.user.username,
            'rating': review.rating,
            'comment': review.comment,
            'is_trusted': review.is_trusted,
            'service_date': review.service_date.strftime('%Y-%m-%d') if review.service_date else None,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'provider': {
            'id': provider.id,
            'name': provider.name,
            'phone': provider.phone_number,
            'email': provider.email,
            'category': provider.category.name,
            'address': provider.address,
            'experience_years': provider.experience_years,
            'rating': provider.rating,
            'total_reviews': provider.total_reviews,
        },
        'trusted_by': trusted_friends,
        'recent_reviews': reviews_data
    })

def populate_fake_data(request):
    """Populate database with fake data for testing"""
    
    # Create service categories
    categories_data = [
        {'name': 'Plumber', 'description': 'Expert plumbing services for leaks, installations, and repairs.'},
        {'name': 'Barber', 'description': 'Professional hairstyling and grooming services at your convenience.'},
        {'name': 'Carpenter', 'description': 'Skilled carpenters for furniture, repairs, and custom projects.'},
        {'name': 'Electrician', 'description': 'Certified electricians for installations, repairs, and maintenance.'},
        {'name': 'AC Service/Repair', 'description': 'Professional AC maintenance, servicing, and repair solutions.'},
        {'name': 'Appliance Repair', 'description': 'Expert repair services for all your home appliances.'}
    ]
    
    created_categories = 0
    for cat_data in categories_data:
        category, created = ServiceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            created_categories += 1
    
    # Create fake service providers
    providers_data = [
        {'name': 'Raj Kumar', 'phone': '+91-9876543210', 'category': 'Plumber', 'rating': 4.5, 'experience': 5, 'address': 'Sector 22, Patiala'},
        {'name': 'Suresh Singh', 'phone': '+91-9876543211', 'category': 'Plumber', 'rating': 4.2, 'experience': 3, 'address': 'Urban Estate, Patiala'},
        {'name': 'Hair Studio - Amit', 'phone': '+91-9876543212', 'category': 'Barber', 'rating': 4.8, 'experience': 7, 'address': 'Mall Road, Patiala'},
        {'name': 'Style Cut - Rohit', 'phone': '+91-9876543213', 'category': 'Barber', 'rating': 4.3, 'experience': 4, 'address': 'Leela Bhawan, Patiala'},
        {'name': 'Wood Works - Ramesh', 'phone': '+91-9876543214', 'category': 'Carpenter', 'rating': 4.6, 'experience': 8, 'address': 'Bahadurgarh Road, Patiala'},
        {'name': 'AC Master - Vikram', 'phone': '+91-9876543215', 'category': 'AC Service/Repair', 'rating': 4.4, 'experience': 6, 'address': 'Sirhind Road, Patiala'},
    ]
    
    created_providers = 0
    for provider_data in providers_data:
        try:
            category = ServiceCategory.objects.get(name=provider_data['category'])
            provider, created = ServiceProvider.objects.get_or_create(
                phone_number=provider_data['phone'],
                defaults={
                    'name': provider_data['name'],
                    'category': category,
                    'rating': provider_data['rating'],
                    'experience_years': provider_data['experience'],
                    'total_reviews': 10,
                    'address': provider_data['address']
                }
            )
            if created:
                created_providers += 1
        except ServiceCategory.DoesNotExist:
            continue
    
    return JsonResponse({
        'message': 'Fake data populated successfully!',
        'categories_created': created_categories,
        'providers_created': created_providers,
        'total_categories': ServiceCategory.objects.count(),
        'total_providers': ServiceProvider.objects.count()
    })