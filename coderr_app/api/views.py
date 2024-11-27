
from rest_framework import viewsets, filters
from coderr_app.models import Profile, Offer, Order, OfferDetail, Review
from .serializers import ProfileSerializer, UserSerializer, OfferSerializer, OrderSerializer, OfferDetailSerializer, ReviewSerializer, BusinessSerializer, CustomerSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Min
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from .permissions import IsBusinessUserOrReadOnly, IsReviewerOrAdmin
from decimal import Decimal
from coderr_app.api import serializers


class BaseInfo(APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        # Anzahl der Bewertungen
        review_count = Review.objects.count()

        # Durchschnittliche Bewertung berechnen und auf eine Dezimalstelle runden
        average_rating_data = Review.objects.aggregate(
            average_rating=Avg("rating"))
        average_rating = average_rating_data.get("average_rating") or 0.0
        # Runde auf eine Dezimalstelle
        average_rating = round(Decimal(average_rating), 1)

        # Anzahl der Business-Profile
        business_profile_count = Profile.objects.filter(
            type="business").count()

        # Anzahl der Angebote
        offer_count = Offer.objects.count()

        # Daten sammeln
        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }

        return Response(data, status=status.HTTP_200_OK)


class OrderCountView(APIView):
    def get(self, request, business_user_id):
        # Filter für laufende Bestellungen (`in_progress`)
        order_count = Order.objects.filter(
            business_user_id=business_user_id, status="in_progress").count()

        if not Profile.objects.filter(user=business_user_id).exists():
            return Response({"error": "Business user not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"order_count": order_count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    def get(self, request, business_user_id):
        # Filter für abgeschlossene Bestellungen (`completed`)
        completed_order_count = Order.objects.filter(
            business_user_id=business_user_id, status="completed").count()

        if not Profile.objects.filter(user=business_user_id).exists():
            return Response({"error": "Business user not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"completed_order_count": completed_order_count}, status=status.HTTP_200_OK)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 6  # Standard Anzahl pro Seite
    page_size_query_param = 'page_size'  # Parameter Anzahl pro Seite
    max_page_size = 100


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business_user', 'reviewer']
    ordering_fields = ['updated_at', 'rating']

    def get_queryset(self):
        """
        Optionally restrict the returned reviews based on query parameters.
        """
        queryset = super().get_queryset()

        # Optional: Filter by business_user_id or reviewer_id from query parameters
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)

        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user

        # Ensure the user is authenticated
        if not user.is_authenticated:
            raise AuthenticationFailed("You must be logged in to create a review.")

        # Ensure the user has a customer profile
        profile = getattr(user, 'profile', None)
        if not profile or profile.type != 'customer':
            raise PermissionDenied("Only users with a customer profile can create reviews.")

        # Extract and validate `business_user` from the request data
        business_user_id = self.request.data.get('business_user')
        if not business_user_id:
            raise serializers.ValidationError({"business_user": "This field is required."})

        try:
            business_user = User.objects.get(id=business_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"business_user": "Invalid business_user ID."})

        # Ensure the target user has a business profile
        business_profile = getattr(business_user, 'profile', None)
        if not business_profile or business_profile.type != 'business':
            raise serializers.ValidationError({"business_user": "The target user must have a business profile."})

        # Check if the reviewer has already left a review for the business user
        if Review.objects.filter(reviewer=user, business_user=business_user).exists():
            raise serializers.ValidationError(
                {"detail": "You can only leave one review per business user."}
            )

        # Save the review with the correct reviewer and business user
        serializer.save(reviewer=user, business_user=business_user)



class OfferDetailsViewSet(viewsets.ModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    # permission_classes = [IsAuthenticated, IsBusinessUserOrReadOnly]
    permission_classes = [AllowAny]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Nur authentifizierte Benutzer
    pagination_class = None  # Optional, wenn keine Paginierung benötigt wird

    def get_queryset(self):
        # Filtert Bestellungen, bei denen der Benutzer beteiligt ist
        user = self.request.user
        queryset = Order.objects.filter(
            customer_user=user) | Order.objects.filter(business_user=user)
        return queryset.order_by('-created_at')


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsBusinessUserOrReadOnly]
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtieren nach creator_id (Benutzer, der das Angebot erstellt hat)
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user_id=creator_id)

       # Annotiere Mindestpreis und maximale Lieferzeit von OfferDetails
        queryset = queryset.annotate(
            min_price=Min('details__price'),  # Minimaler Preis aus OfferDetail
            # Maximale Lieferzeit aus OfferDetail
            # max_delivery_time=Max('details__delivery_time_in_days')
            min_delivery_time=Min('details__delivery_time_in_days')
        )

        # Filtern nach Mindestpreis
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(min_price__lte=min_price)

        # Filtern nach maximaler Lieferzeit
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            queryset = queryset.filter(
                min_delivery_time__lte=max_delivery_time)

        return queryset

    def list(self, request, *args, **kwargs):
        # Überprüfen, ob ein Suchbegriff vorhanden ist
        search_query = request.query_params.get('search', '').strip()
        page_param = request.query_params.get('page', '').strip()
        max_delivery_time = request.query_params.get('max_delivery_time').strip()

        # Wenn ein Suchbegriff oder Filter vorhanden ist und `page` angegeben ist
        if (search_query or max_delivery_time) and page_param:
            # Entfernen des `page`-Parameters, um Fehler zu vermeiden
            request.query_params._mutable = True  # QueryDict auf "änderbar" setzen
            request.query_params.pop('page', None)  # Entfernen Sie `page`            
            request.query_params._mutable = False  # Zurück auf unveränderlich setzen

        # Aufruf der Standard-Logik
        return super().list(request, *args, **kwargs)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def retrieve(self, request, *args, **kwargs):

        try:

            # `pk` wird hier der `user_id` entsprechen
            user_id = kwargs.get('pk')
            profile = get_object_or_404(Profile, user__id=user_id)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)
    

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user_id = kwargs.get('pk')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        try:
            user = User.objects.get(pk=user_id)
            serializer = UserSerializer(
                user, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()

            profile = Profile.objects.get(user__id=user_id)
            serializer = ProfileSerializer(
                profile, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)


class BusinessProfilesView(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        if pk:  # Wenn eine Profil-ID übergeben wurde, Detailansicht anzeigen
            try:
                profile = Profile.objects.get(user__pk=pk, type="business")
                serializer = BusinessSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Profile.DoesNotExist:
                return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Andernfalls alle Business-Profile auflisten
        business_profiles = Profile.objects.filter(type="business")
        serializer = BusinessSerializer(business_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerProfilesView(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        if pk:  # Wenn eine Profil-ID übergeben wurde, Detailansicht anzeigen
            try:
                profile = Profile.objects.get(user__pk=pk, type="customer")
                serializer = CustomerSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Profile.DoesNotExist:
                return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Andernfalls alle Business-Profile auflisten
        business_profiles = Profile.objects.filter(type="customer")
        serializer = CustomerSerializer(business_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
