from django.db import models
from users.models import User

class ServiceCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    contact_info = models.CharField(max_length=100)

    def __str__(self):
        return self.name
