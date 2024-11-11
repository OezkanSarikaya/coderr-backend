
from rest_framework import viewsets, generics, permissions, filters
from coderr_app.models import Profile
from .serializers import ProfileSerializer, UserPatchSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


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