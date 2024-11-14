
from rest_framework import viewsets, filters, generics, permissions
from coderr_app.models import Profile, Offer, Order, OfferDetail, Review
from .serializers import ProfileSerializer, UserSerializer, OfferSerializer, OrderSerializer, OfferDetailSerializer, ReviewSerializer, ProfileTypeSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.views import APIView
# from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User
# from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny

class BaseInfo(APIView):
    permission_classes = [AllowAny] 
    def get(self, *args, **kwargs):
        # Filter für laufende Bestellungen (`in_progress`)
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(Avg("rating", default=0))
        average_rating = average_rating.get("average_rating") or 0.0
        business_profile_count = Profile.objects.filter(type="business").count()
        offer_count = Offer.objects.count()
        
        
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
        order_count = Order.objects.filter(business_user_id=business_user_id, status="in_progress").count()
        
        if order_count == 0 and not Order.objects.filter(business_user_id=business_user_id).exists():
            return Response({"error": "Business user not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"order_count": order_count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    def get(self, request, business_user_id):
        # Filter für abgeschlossene Bestellungen (`completed`)
        completed_order_count = Order.objects.filter(business_user_id=business_user_id, status="completed").count()
        
        if completed_order_count == 0 and not Order.objects.filter(business_user_id=business_user_id).exists():
            return Response({"error": "Business user not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"completed_order_count": completed_order_count}, status=status.HTTP_200_OK)

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 5  # Standard Anzahl pro Seite
    page_size_query_param = 'page_size'  # Parameter Anzahl pro Seite
    max_page_size = 100


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]   
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['updated_at','rating']

    def perform_create(self, serializer):
        # Überprüfen, ob der Benutzer authentifiziert ist
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed("You must be logged in to create a review.")
        
        # Falls der Benutzer authentifiziert ist, setze den reviewer auf self.request.user
        serializer.save(reviewer=self.request.user)


class OfferDetailsViewSet(viewsets.ModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [AllowAny] 
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]    
    # filterset_fields = {
    #     'user': ['exact'],  # Filter für den 'creator_id' (user ID des Erstellers)
    #     'details__price': ['gte'],  # Mindestpreis für die OfferDetails (min_price)
    #     'details__delivery_time_in_days': ['lte'],  # Maximale Lieferzeit (max_delivery_time)
    # }
    ordering_fields = ['updated_at','details__price']
    search_fields = ['title', 'description']    

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtieren nach creator_id (Benutzer, der das Angebot erstellt hat)
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user_id=creator_id)

        # Filtern nach Mindestpreis in OfferDetails
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(details__price__gte=min_price)

        # Filtern nach maximaler Lieferzeit in OfferDetails
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            queryset = queryset.filter(details__delivery_time_in_days__lte=max_delivery_time)

        return queryset


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

    # @action(detail=True, methods=['patch'])

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
    # permission_classes = [IsAuthenticated]  # Nur authentifizierte Benutzer können die Liste sehen

    def get(self, request, *args, **kwargs):
        business_profiles = Profile.objects.filter(type="business")
        serializer = ProfileTypeSerializer(business_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerProfilesView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        customer_profiles = Profile.objects.filter(type="customer")
        serializer = ProfileTypeSerializer(customer_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
