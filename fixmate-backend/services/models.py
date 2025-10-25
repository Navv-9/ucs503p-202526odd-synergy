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
    _id = models.ObjectIdField(primary_key=True, db_column='_id')  # Make it primary key
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    category_name = models.CharField(max_length=100, default='Unknown', blank=True)
    rating = models.FloatField(default=0.0)
    original_rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    experience_years = models.IntegerField(default=0)
    address = models.TextField()

    class Meta:
        db_table = 'service_provider'
    
    @property
    def id(self):
        """Return string representation of _id"""
        return str(self._id) if self._id else None
    
    def save(self, *args, **kwargs):
        """Ensure _id exists before saving"""
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
    
    class Meta:
        db_table = 'user_profile'
    
    def __str__(self):
        return self.user.username


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
    provider_id = models.CharField(max_length=24)  # Store ObjectId as string
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
    _id = models.ObjectIdField(primary_key=True, db_column='_id')  # Use ObjectId as primary key
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider_id = models.CharField(max_length=24)  # Store ObjectId as string
    booking_date = models.DateField()
    booking_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'services_booking'  # Match your MongoDB collection name
    
    @property
    def id(self):
        """Return string representation of _id"""
        return str(self._id) if self._id else None
    
    def save(self, *args, **kwargs):
        """Ensure _id exists before saving"""
        if not self._id:
            self._id = ObjectId()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - Provider {self.provider_id} ({self.booking_date})"