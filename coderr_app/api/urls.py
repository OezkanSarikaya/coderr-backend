from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, BusinessProfilesView, CustomerProfilesView


router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
urlpatterns = [
    path('', include(router.urls)),
    # path('profile/<int:user>/', ProfileViewSet.as_view, name='profile-detail'),
    path('profiles/business/', BusinessProfilesView.as_view(), name='business_profiles'),
    path('profiles/customer/', CustomerProfilesView.as_view(), name='customer_profiles'),
]


