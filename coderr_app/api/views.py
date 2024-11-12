
from rest_framework import viewsets, filters #, generics, permissions, filters
from coderr_app.models import Profile, Offer, Order, OfferDetail, Review
from .serializers import ProfileSerializer, UserSerializer, OfferSerializer, OrderSerializer, OfferDetailSerializer, ReviewSerializer
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
# from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User
# from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 5 # Standard Anzahl pro Seite
    page_size_query_param = 'page_size' # Parameter Anzahl pro Seite
    max_page_size = 100

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class OfferDetailsViewSet(viewsets.ModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['updated_at'] 
    search_fields = ['title','description'] 
#     # permission_classes = [IsAuthenticated]

#     def get(self, request, pk):
#         try:
#             profile = Profile.objects.get(pk=pk)
#             serializer = ProfileSerializer(profile)
#             return Response(serializer.data)
#         except Profile.DoesNotExist:
#             raise NotFound("Profil nicht gefunden")

#     def patch(self, request, pk):
#         try:
#             profile = Profile.objects.get(pk=pk)
#         except Profile.DoesNotExist:
#             raise NotFound("Profil nicht gefunden")

#         # Ermögliche es, dass 'first_name' und 'last_name' geändert werden können
#         serializer = ProfileSerializer(profile, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def retrieve(self, request, *args, **kwargs):

        try:
  
            user_id = kwargs.get('pk')  # `pk` wird hier der `user_id` entsprechen
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
            serializer = UserSerializer(user, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
            
            profile = Profile.objects.get(user__id=user_id)
            serializer = ProfileSerializer(profile, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)


    # def get_serializer_class(self):
    #     # Wenn die Anfrage eine PATCH-Methode ist, verwende den ProfilePatchSerializer
    #     if self.action == 'partial_update':  # "partial_update" ist die Aktion für PATCH
    #         return UserPatchSerializer
    #     # Sonst den normalen ProfileSerializer verwenden
    #     return ProfileSerializer
    
class BusinessProfilesView(APIView):
    # permission_classes = [IsAuthenticated]  # Nur authentifizierte Benutzer können die Liste sehen

    def get(self, request, *args, **kwargs):
        business_profiles = Profile.objects.filter(type="business")
        serializer = ProfileSerializer(business_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomerProfilesView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        customer_profiles = Profile.objects.filter(type="customer")
        serializer = ProfileSerializer(customer_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)