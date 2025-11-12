from djongo import models
from django.contrib.auth.models import User
from bson import ObjectId

class ServiceCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'service_category'
    
    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    _id = models.ObjectIdField(primary_key=True, db_column='_id')
    
    # NEW: Link to user account
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile', null=True, blank=True)
    
    # Existing fields
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    category_name = models.CharField(max_length=100, default='Unknown', blank=True)
    rating = models.FloatField(default=0.0)
    original_rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    experience_years = models.IntegerField(default=0)
    address = models.TextField()
    
    # NEW: Provider-specific fields
    description = models.TextField(blank=True, default='')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    availability = models.CharField(max_length=200, blank=True, default='Mon-Sat, 9AM-6PM')
    service_area = models.CharField(max_length=200, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    
    class Meta:
        db_table = 'service_provider'
    
    @property
    def id(self):
        return str(self._id) if self._id else None
    
    def save(self, *args, **kwargs):
        if not self._id:
            self._id = ObjectId()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.category_name}"

class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    
    # NEW: User type fields
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
        ('both', 'Both'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    is_provider = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'user_profile'
    
    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'contact'
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider_id = models.CharField(max_length=24)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    is_trusted = models.BooleanField(default=False)
    service_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review'
    
    def __str__(self):
        return f"{self.user.username} - Provider {self.provider_id} ({self.rating}★)"


class Booking(models.Model):
    _id = models.ObjectIdField(primary_key=True, db_column='_id')
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider_id = models.CharField(max_length=24)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    provider_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completion_notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'services_booking'
    
    @property
    def id(self):
        return str(self._id) if self._id else None
    
    def save(self, *args, **kwargs):
        if not self._id:
            self._id = ObjectId()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - Provider {self.provider_id} ({self.booking_date})"