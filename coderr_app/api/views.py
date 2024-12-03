"""
Views for the Coderr backend.

These classes handle requests for profiles, offers, orders, reviews, and
additional application data. They use Django Rest Framework (DRF) to manage
serializers, permissions, and querysets.
"""

from rest_framework import viewsets, filters, status
from coderr_app.models import Profile, Offer, Order, OfferDetail, Review
from .serializers import ProfileSerializer, UserSerializer, OfferSerializer, OrderSerializer, OfferDetailSerializer, ReviewSerializer, BusinessSerializer, CustomerSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Min
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from .permissions import IsBusinessUserOrReadOnly, IsReviewerOrAdmin, IsAuthenticatedOrReadOnlyForProfile, IsOwnerOrReadOnly
from decimal import Decimal
from coderr_app.api import serializers
from math import ceil


class BaseInfo(APIView):
    """
    Provides general application statistics like review count, average ratings,
    number of business profiles, and total offers.
    """
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        # Total number of reviews
        review_count = Review.objects.count()

        # Calculate and round average rating to one decimal place
        average_rating_data = Review.objects.aggregate(
            average_rating=Avg("rating"))
        average_rating = average_rating_data.get("average_rating") or 0.0
        average_rating = round(Decimal(average_rating), 1)

        # Count of business profiles
        business_profile_count = Profile.objects.filter(
            type="business").count()

        # Count of offers
        offer_count = Offer.objects.count()

        # Collect the data
        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }

        return Response(data, status=status.HTTP_200_OK)


class OrderCountView(APIView):
    """
    Provides the count of in-progress orders for a specific business user.
    """

    def get(self, request, business_user_id):
        # Count orders with status "in_progress"
        order_count = Order.objects.filter(
            business_user_id=business_user_id, status="in_progress").count()

        # Check if the business user exists
        if not Profile.objects.filter(user=business_user_id).exists():
            return Response({"error": "Business user not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"order_count": order_count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """
    Provides the count of completed orders for a specific business user.
    """

    def get(self, request, business_user_id):
        # Count orders with status "completed"
        completed_order_count = Order.objects.filter(
            business_user_id=business_user_id, status="completed").count()

        # Check if the business user exists
        if not Profile.objects.filter(user=business_user_id).exists():
            return Response({"error": "Business user not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"completed_order_count": completed_order_count}, status=status.HTTP_200_OK)


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination class for large datasets. Default page size is 6, and the maximum is 100.
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for reviews. Reviews can only be created by authenticated
    users with a customer profile.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewerOrAdmin]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business_user', 'reviewer']
    ordering_fields = ['updated_at', 'rating']

    def get_queryset(self):
        """
        Optionally restrict the returned reviews based on query parameters.
        """
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)

        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        return queryset

    def perform_create(self, serializer):
        """
        Handles validation and creation of a new review.
        """
        user = self.request.user

        if not user.is_authenticated:
            raise AuthenticationFailed(
                "You must be logged in to create a review.")

        profile = getattr(user, 'profile', None)
        if not profile or profile.type != 'customer':
            raise PermissionDenied(
                "Only users with a customer profile can create reviews.")

        business_user_id = self.request.data.get('business_user')
        if not business_user_id:
            raise serializers.ValidationError(
                {"business_user": "This field is required."})

        try:
            business_user = User.objects.get(id=business_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"business_user": "Invalid business_user ID."})

        business_profile = getattr(business_user, 'profile', None)
        if not business_profile or business_profile.type != 'business':
            raise serializers.ValidationError(
                {"business_user": "The target user must have a business profile."})

        if Review.objects.filter(reviewer=user, business_user=business_user).exists():
            raise serializers.ValidationError(
                {"detail": "You can only leave one review per business user."}
            )

        serializer.save(reviewer=user, business_user=business_user)


class OfferDetailsViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for offer details. Accessible by any user.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [AllowAny]


class OrderViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for orders. Only authenticated users can access.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination

    def get_queryset(self):
        """
        Filters orders to include only those where the user is involved.
        """
        user = self.request.user
        queryset = Order.objects.filter(
            customer_user=user) | Order.objects.filter(business_user=user)
        return queryset.order_by('-created_at')


class OfferViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for offers.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsBusinessUserOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']

    def create(self, request, *args, **kwargs):
        """
        Override create to customize the response with full details.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate the incoming data
        self.perform_create(serializer)

        # Fetch the created offer instance
        offer = serializer.instance

        # Use OfferSerializer with full details for the response
        response_serializer = OfferSerializer(offer, context={'request': request})

        # Debugging: Output the response data
        print("DEBUG - Response data:", response_serializer.data)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """
        Save the offer with the associated details.
        """
        serializer.save()

    """
    Handles CRUD operations for offers. Only business users can modify offers.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsBusinessUserOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']

    def get_queryset(self):
        """
        Filters offers based on query parameters like creator ID, minimum price, or delivery time.
        """
        queryset = super().get_queryset().prefetch_related('details')
        creator_id = self.request.query_params.get('creator_id')

        if creator_id:
            queryset = queryset.filter(user_id=creator_id)

        queryset = queryset.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )

        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(min_price__lte=min_price)

        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            queryset = queryset.filter(min_delivery_time__lte=max_delivery_time)

        return queryset

    def perform_create(self, serializer):
        """
        Save the offer and related details during creation.
        """
        offer = serializer.save(user=self.request.user)
        print("DEBUG - Offer created:", offer)  # Debugging: Inspect created offer object

    def create(self, request, *args, **kwargs):
        """
        Override create method to debug serializer data and handle headers correctly.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        print("DEBUG - Serializer data after save:", serializer.data)  # Debugging
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_success_headers(self, data):
        """
        Generate headers for successful creation responses.
        """
        try:
            return {'Location': str(data.get('id', ''))}
        except KeyError:
            return {}


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for profiles. Only profile owners can update their profile.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnlyForProfile]

    def get_object(self):
        """
        Ensures that the profile permission is checked.
        """
        user_id = self.kwargs.get('pk')
        profile = get_object_or_404(Profile, user__id=user_id)
        self.check_object_permissions(
            self.request, profile)  # Prüft Permissions
        return profile

    def retrieve(self, request, *args, **kwargs):
        """
        Fetches the profile based on the user ID (`pk`).
        """
        user_id = kwargs.get('pk')
        profile = get_object_or_404(Profile, user__id=user_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Overwrites the update to update both profiles and user fields.
        """
        partial = kwargs.pop('partial', False)
        profile = self.get_object()  # gets profile (incl. Permission-Check)
        user = profile.user  # gets user of the profile

        # validate profile serializer
        profile_serializer = self.get_serializer(
            profile, data=request.data, partial=partial)
        profile_serializer.is_valid(raise_exception=True)

        # update user fields
        user_data = {}
        if 'first_name' in request.data:
            user_data['first_name'] = request.data['first_name']
        if 'last_name' in request.data:
            user_data['last_name'] = request.data['last_name']
        if 'username' in request.data:
            user_data['username'] = request.data['username']

        if user_data:
            user_serializer = UserSerializer(
                user, data=user_data, partial=partial)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                raise ValidationError(user_serializer.errors)

        # save changes of profile
        self.perform_update(profile_serializer)

        return Response(profile_serializer.data)


class BusinessProfilesView(APIView):
    """
    Shows list or single business profiles.
    """
    def get(self, request, pk=None, *args, **kwargs):
        if pk:  # If a profile ID is provided, show details
            try:
                profile = Profile.objects.get(user__pk=pk, type="business")
                serializer = BusinessSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Profile.DoesNotExist:
                return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Otherwise, list all business profiles
        business_profiles = Profile.objects.filter(type="business")
        serializer = BusinessSerializer(business_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerProfilesView(APIView):
    """
    Shows list or single customer profiles.
    """
    
    def get(self, request, pk=None, *args, **kwargs):
        if pk:  # If a profile ID is provided, show details
            try:
                profile = Profile.objects.get(user__pk=pk, type="customer")
                serializer = CustomerSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Profile.DoesNotExist:
                return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Otherwise, list all customer profiles
        business_profiles = Profile.objects.filter(type="customer")
        serializer = CustomerSerializer(business_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
