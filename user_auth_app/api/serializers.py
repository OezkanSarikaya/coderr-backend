# user_auth_app/api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from coderr_app.models import Profile


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    # Optionales Feld für den Typ
    type = serializers.ChoiceField(
        choices=Profile.TYPE_CHOICES, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate(self, data):
        # Passwortvalidierung
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({
                "password": ["Das Passwort ist nicht gleich mit dem wiederholten Passwort"]
            })

        # Email-Validierung
        if 'email' not in data or not data['email']:
            raise serializers.ValidationError({
                "email": ["E-Mail ist erforderlich."]
            })

        return data

    def validate_email(self, value):
        # Überprüfung, ob die E-Mail bereits existiert
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Ein Benutzer mit dieser E-Mail existiert bereits.")

        return value

    def validate_username(self, value):
        # Überprüfung, ob der Benutzername bereits existiert
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                {"username": ["Dieser Benutzername ist bereits vergeben."]})

        return value

    def save(self):
        # Benutzer erstellen
        account = User(
            email=self.validated_data['email'],
            username=self.validated_data['username']
        )
        account.set_password(self.validated_data['password'])
        account.save()

        # Profil erstellen und verknüpfen
        profile_type = self.validated_data.get('type', 'customer')
        Profile.objects.create(
            user=account, email=account.email, type=profile_type)

        return account
