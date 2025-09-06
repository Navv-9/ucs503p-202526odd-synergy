# from django.db import models
# from users.models import User

# class ServiceCategory(models.Model):
#     name = models.CharField(max_length=50)

#     def __str__(self):
#         return self.name


# class ServiceProvider(models.Model):
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
#     contact_info = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name

from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom User model (so we can extend later)
class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    contacts = models.ManyToManyField("self", blank=True, symmetrical=False)  
    # contacts = all users I know (friends/social layer)

    def _str_(self):
        return self.username


class ServiceProvider(models.Model):
    name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=100)  # e.g. plumber, barber
    contact_info = models.CharField(max_length=255)

    def _str_(self):
        return f"{self.name} ({self.service_type})"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(default=0)  # 1–5 stars
    trusted = models.BooleanField(default=False)  # thumbs up = trusted
    comment = models.TextField(blank=True)

    def _str_(self):
        return f"{self.user.username} → {self.provider.name}"