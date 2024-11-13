from django.contrib import admin
from .models import Profile, Offer, Order, OfferDetail, Review

# Register your models here.

admin.site.register(Profile)
admin.site.register(Offer)
admin.site.register(Order)
admin.site.register(OfferDetail)
admin.site.register(Review)
