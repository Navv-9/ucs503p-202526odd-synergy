from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    avatar_url = models.URLField(blank=True, null=True)
    contacts = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.username


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_provider = models.ForeignKey("services.ServiceProvider", on_delete=models.CASCADE)
    thumbs_up = models.BooleanField(default=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.service_provider.name}"
