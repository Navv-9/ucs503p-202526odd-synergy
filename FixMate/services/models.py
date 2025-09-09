# services/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"

class Contact(models.Model):
    """Store user's contacts for social layer"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    is_registered = models.BooleanField(default=False)
    registered_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacted_by')
    
    class Meta:
        unique_together = ['user', 'contact_phone']
    
    def __str__(self):
        return f"{self.user.username}'s contact: {self.contact_name}"

class ServiceCategory(models.Model):
    """Service categories like Plumber, Barber, etc."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=200, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Service Categories"
    
    def __str__(self):
        return self.name

class ServiceProvider(models.Model):
    """Individual service providers"""
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='providers')
    address = models.TextField(max_length=200, blank=True)
    experience_years = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.category.name}"

class Review(models.Model):
    """Reviews and trust system"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=500, blank=True)
    is_trusted = models.BooleanField(default=False)  # Thumbs up/down
    service_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'provider']  # One review per user per provider
    
    def __str__(self):
        return f"{self.user.username} -> {self.provider.name} ({self.rating}★)"

class Booking(models.Model):
    """Track bookings/appointments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField()
    status_choices = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    notes = models.TextField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} -> {self.provider.name} on {self.booking_date.date()}"