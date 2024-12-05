"""
URL configuration for the Coderr backend.

This file maps the endpoints of the application to their respective views.
It uses the Django Rest Framework's (DRF) `DefaultRouter` for standard routes
and custom paths for additional functionality.

The Coderr backend serves endpoints for managing user profiles, offers, orders,
and reviews. It also provides utility endpoints like order counts and base information.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, BusinessProfilesView, CustomerProfilesView, OfferViewSet, OrderViewSet, OfferDetailsViewSet, ReviewViewSet, OrderCountView, CompletedOrderCountView, BaseInfo, OfferDetailView

# Create a router for standard viewsets
router = DefaultRouter()

# Register viewsets with the router
router.register(r'profile', ProfileViewSet, basename='profile')
"""Handles CRUD operations for user profiles."""

router.register(r'offers', OfferViewSet, basename='offer')
"""Handles CRUD operations for business offers."""

router.register(r'offerdetails', OfferDetailsViewSet, basename='offerdetails')
"""Handles operations for detailed offer information."""

router.register(r'orders', OrderViewSet, basename='order')
"""Handles CRUD operations for customer orders."""

router.register(r'reviews', ReviewViewSet, basename='reviews')
"""Handles CRUD operations for reviews of business users."""

# Define additional custom URL patterns
urlpatterns = [
    # Include the router's automatically generated routes
    path('', include(router.urls)),

    # Endpoints for business user profiles
    path('profiles/business/', BusinessProfilesView.as_view(),
         name='business_profiles'),
    path('profiles/business/<int:pk>/', BusinessProfilesView.as_view(),
         name='business_profile_detail'),

    # Endpoints for customer user profiles
    path('profiles/customer/', CustomerProfilesView.as_view(),
         name='customer_profiles'),
    path('profiles/customer/<int:pk>/', CustomerProfilesView.as_view(),
         name='customer_profile_detail'),

    # Endpoints for order counts
    path('order-count/<int:business_user_id>/',
         OrderCountView.as_view(), name='order_count'),
    path('completed-order-count/<int:business_user_id>/',
         CompletedOrderCountView.as_view(), name='completed_order_count'),

    # Endpoint for general application base information
    path('base-info/', BaseInfo.as_view(), name='base-info'),
#     path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
   
    
]
