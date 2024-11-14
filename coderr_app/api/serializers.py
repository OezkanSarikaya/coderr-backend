from rest_framework import serializers
from coderr_app.models import Profile, Offer, Order, OfferDetail, Review
from django.contrib.auth.models import User
from django.conf import settings  # Für Zugriff auf MEDIA_URL
from django.urls import reverse
from django.db.models import Min

class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        # Dynamisch den URL-Pfad für jedes OfferDetail-Objekt erstellen
        return reverse('offerdetails-detail', args=[obj.id])


class ReviewSerializer(serializers.ModelSerializer):

    reviewer = serializers.ReadOnlyField(source='reviewer.id')
    class Meta:
        model = Review
        # fields = '__all__'
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'username' ]

class ProfileTypeSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Hier verschachtelter User-Serializer
    file = serializers.FileField(required=False)

    class Meta:
        model = Profile
        fields = [
            'user',           # Benutzerinformationen als verschachteltes Objekt
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
            'file': {'required': False}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Füge den relativen Pfad für das `file`-Feld hinzu, falls vorhanden
        if instance.file:
            representation['file'] = f"{settings.MEDIA_URL}{instance.file}"

        return representation
    


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    # details = OfferDetailLinkSerializer(many=True, read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    # details = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='offers')
    class Meta:
        model = Offer
        # fields = '__all__'
        # fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price','min_delivery_time', 'user_details']
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]
    
    def get_min_price(self, obj):
        # Minimum Preis von den OfferDetails berechnen
        return obj.details.aggregate(min_price=Min('price'))['min_price']

    def get_min_delivery_time(self, obj):
        # Minimum Lieferzeit von den OfferDetails berechnen
        return obj.details.aggregate(min_delivery_time=Min('delivery_time_in_days'))['min_delivery_time']
    
    
    def validate_revisions(self, value):
        if value < -1:
            raise serializers.ValidationError("Die Anzahl der Revisionen muss -1 oder größer sein.")
        return value

    def validate_delivery_time_in_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Die Lieferzeit muss ein positiver Wert sein.")
        return value

    def validate_features(self, value):
        if not value:
            raise serializers.ValidationError("Mindestens ein Feature muss angegeben werden.")
        return value

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Es müssen genau drei Angebotsdetails vorhanden sein.")

        offer_types = {detail['offer_type'] for detail in value}
        if offer_types != {'basic', 'standard', 'premium'}:
            raise serializers.ValidationError("Die Angebotsdetails müssen genau die Typen 'basic', 'standard' und 'premium' enthalten.")
        
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        
        return offer





class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # ID des Users
    
    # user = UserSerializer() 
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
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
