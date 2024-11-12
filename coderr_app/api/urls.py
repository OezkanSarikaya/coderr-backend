from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, BusinessProfilesView, CustomerProfilesView, OfferViewSet, OrderViewSet, OfferDetailsViewSet, ReviewViewSet


router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'offerdetails', OfferDetailsViewSet, basename='offerdetails')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='reviews')
urlpatterns = [
    path('', include(router.urls)),
    path('profiles/business/', BusinessProfilesView.as_view(), name='business_profiles'),
    path('profiles/customer/', CustomerProfilesView.as_view(), name='customer_profiles'),
]


