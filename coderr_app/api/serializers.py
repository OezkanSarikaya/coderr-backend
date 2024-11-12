from rest_framework import serializers
from coderr_app.models import Profile, Offer, Order, OfferDetail, Review
from django.contrib.auth.models import User
from django.conf import settings  # Für Zugriff auf MEDIA_URL


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = '__all__'


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())  # ID des Users
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    file = serializers.FileField(required=False)

    class Meta:
        model = Profile
        # fields = '__all__'
        fields = [
            'user',           # Benutzer-ID
            'username',       # Benutzername
            'first_name',     # Vorname
            'last_name',      # Nachname
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at'
        ]
        extra_kwargs = {
            # Das Feld `file` ist nicht erforderlich
            'file': {'required': False}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        user_data = {
            "user": instance.user.id,
            "username": instance.user.username,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name
        }

        representation.update(user_data)
        # Überprüfen, ob das Feld `file` einen Wert hat und füge nur den relativen Pfad hinzu
        if instance.file:
            # MEDIA_URL direkt verwenden, um doppelte URLs zu vermeiden
            representation['file'] = f"{settings.MEDIA_URL}{instance.file}"

        return representation
