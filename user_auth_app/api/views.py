from .serializers import RegistrationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from coderr_app.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


def get_guest_user():
    guest_username = "guest@domain.com"

    # Get or create guestuser
    guest_user, created = User.objects.get_or_create(
        username=guest_username,
        defaults={'is_active': True, 'first_name': 'Guest',
                  'email': "guest@domain.com", }
    )

    if created:
        guest_user.set_unusable_password()  # guestuser withour password
        guest_user.save()

    # get or create token for guestuser
    token, _ = Token.objects.get_or_create(user=guest_user)

    # get or create contact for guestuser
    Profile.objects.get_or_create(
        user=guest_user,
        defaults={
            'email': "guest@domain.com",  # Pseudo-Email for guest
            'name': "Guest User",
        }
    )

    return guest_user, token

"""
Registration: Save userdata and profile and response json for LocalStorage
"""
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
Login: Authenticate User and response json for LocalStorage
"""
class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        is_guest = request.data.get("is_guest", False)
        data = {}

        if is_guest:
            # Gastzugang gewähren
            guest_user, token = get_guest_user()
            data = {
                "token": token.key,
                "username": guest_user.username,
                "email": "guest@domain.com",  # Evtl. als Pseudoe-Mail für Gast
                "name": "Guest User"
            }
            return Response(data, status=status.HTTP_200_OK)

        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'error': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)

        # Falls Login erfolgreich, Token generieren und Contact-Daten abrufen
        token, created = Token.objects.get_or_create(user=user)

        try:
            contact = Profile.objects.get(user=user)
            # contact_data = contact.name  # Beispiel, wenn nur der Name benötigt wird
        except Profile.DoesNotExist:
            contact_data = None

        data = {
            'token': token.key,
            'username': user.username,
            'email': user.email,
            "user_id": user.pk
        }
        return Response(data)
