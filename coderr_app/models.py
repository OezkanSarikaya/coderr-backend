from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    TYPE_CHOICES = [
        ('business','Business'),
        ('customer','Customer'),
    ]
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    tel = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=8,choices=TYPE_CHOICES,blank=True, null=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)


