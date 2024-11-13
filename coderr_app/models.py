from django.db import models
from django.contrib.auth.models import User
# from django.core.validators import MinValueValidator

# Create your models here.
class Review(models.Model):
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.business_user.username} - Rating: {self.rating}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Bearbeitung'),
        ('completed', 'Abgeschlossen'),
        ('cancelled', 'Abgebrochen'),
    ]
    
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_orders')
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=10, choices=[
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ])
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.title} ({self.get_status_display()})"

class Profile(models.Model):
    TYPE_CHOICES = [
        ('business','Business'),
        ('customer','Customer'),
    ]        
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    tel = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=8,choices=TYPE_CHOICES,blank=True, null=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.FileField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # min_price = models.DecimalField(max_digits=6, decimal_places=2)
    # min_delivery_time = models.IntegerField(default=10)

    # @property
    # def details(self):
    #     return self.offerdetail_set.all()
    
    # @property
    # def user_details(self):
    #     return {
    #         "first_name": self.user.first_name,
    #         "last_name": self.user.last_name,
    #         "username": self.user.username,
    #     }
    
    # def __str__(self):
    #     return self.title

class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details', null=True)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(default=-1)
    delivery_time_in_days = models.PositiveIntegerField()  # Nur positive Integer
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()  # Speichert eine Liste von Features als JSON
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.title} ({self.offer_type}) - {self.price}€"

    
