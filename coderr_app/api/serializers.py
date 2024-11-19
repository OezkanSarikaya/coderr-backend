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
        fields = ['id', 'business_user', 'reviewer', 'rating',
                  'description', 'created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True, required=True)  # Write-only Feld

    class Meta:
        model = Order
        # fields = '__all__'
        # fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status',
        #           'created_at', 'updated_at']
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions', 
            'delivery_time_in_days', 'price', 'features', 'offer_type', 
            'status', 'created_at', 'updated_at', 'offer_detail_id'
        ]
        read_only_fields = ['customer_user', 'business_user', 'title', 
                            'revisions', 'delivery_time_in_days', 'price', 
                            'features', 'offer_type']
        
    def validate_offer_detail_id(self, value):
        # Überprüfen, ob das OfferDetail existiert
        try:
            offer_detail = OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError("Invalid offer_detail_id.")
        return value

    def create(self, validated_data):
        # Hole den angemeldeten Benutzer aus dem Kontext
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")

        customer_user = request.user
        offer_detail_id = validated_data.pop('offer_detail_id')

        # Hole das OfferDetail
        offer_detail = OfferDetail.objects.get(id=offer_detail_id)

        # Erstelle die Order basierend auf OfferDetail
        order = Order.objects.create(
            customer_user=customer_user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            **validated_data
        )

        return order


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type']

    def validate(self, data):
        # Revisions dürfen nicht unter -1 sein
        if data['revisions'] < -1:
            raise serializers.ValidationError(
                "Revisions must be -1 or greater.")

        # Die Lieferzeit muss positiv sein
        if data['delivery_time_in_days'] <= 0:
            raise serializers.ValidationError(
                "Delivery time must be a positive integer.")

        # Features müssen mindestens einen Eintrag haben
        if not data['features']:
            raise serializers.ValidationError(
                "At least one feature is required.")

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'username']


class ProfileTypeSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Hier verschachtelter User-Serializer
    file = serializers.FileField(required=False)

    class Meta:
        model = Profile
        fields = [
            'user',           # Benutzerinformationen als verschachteltes Objekt
            'file',
            # 'location',
            # 'tel',
            # 'description',
            # 'working_hours',
            'uploaded_at',
            'type',
            # 'email',
            # 'created_at'
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


# class OfferSerializer(serializers.ModelSerializer):
#     # details = OfferDetailSerializer(many=True)
#     details = OfferDetailLinkSerializer(many=True, read_only=True)
#     details_data = OfferDetailSerializer(many=True, write_only=True, required=True)  # für POST genutzt
#     user_details = UserSerializer(source='user', read_only=True)
#     min_price = serializers.SerializerMethodField()
#     min_delivery_time = serializers.SerializerMethodField()
#     # details = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='offers')
#     class Meta:
#         model = Offer
#         # fields = '__all__'
#         # fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price','min_delivery_time', 'user_details']
#         fields = [
#             'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
#             'details', 'min_price', 'min_delivery_time', 'user_details','details_data'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Wenn der Aufruf ein POST ist, setzen wir `details_data` auf erforderlich
#         if self.context.get('request') and self.context['request'].method == 'POST':
#             self.fields['details_data'].required = True

#     # def get_details(self, instance):
#     #     # Generiere URLs für GET (read-only)
#     #     return [{"id": detail.id, "url": f"/offerdetails/{detail.id}/"} for detail in instance.details.all()]


#     def get_min_price(self, obj):
#         # Minimum Preis von den OfferDetails berechnen
#         return obj.details.aggregate(min_price=Min('price'))['min_price']

#     def get_min_delivery_time(self, obj):
#         # Minimum Lieferzeit von den OfferDetails berechnen
#         return obj.details.aggregate(min_delivery_time=Min('delivery_time_in_days'))['min_delivery_time']


#     # def validate_revisions(self, value):
#     #     if value < -1:
#     #         raise serializers.ValidationError("Die Anzahl der Revisionen muss -1 oder größer sein.")
#     #     return value

#     # def validate_delivery_time_in_days(self, value):
#     #     if value <= 0:
#     #         raise serializers.ValidationError("Die Lieferzeit muss ein positiver Wert sein.")
#     #     return value

#     # def validate_features(self, value):
#     #     if not value:
#     #         raise serializers.ValidationError("Mindestens ein Feature muss angegeben werden.")
#     #     return value

#     # def validate_details(self, value):
#     #     # Überprüfen, ob genau drei Details vorhanden sind
#     #     if len(value) != 3:
#     #         raise serializers.ValidationError("Es müssen genau drei Angebotsdetails vorhanden sein.")

#     #     # Überprüfen, ob die offer_types basic, standard und premium abgedeckt sind
#     #     offer_types = {detail['offer_type'] for detail in value}
#     #     if offer_types != {'basic', 'standard', 'premium'}:
#     #         raise serializers.ValidationError("Die Angebotsdetails müssen genau die Typen 'basic', 'standard' und 'premium' enthalten.")

#     #     return value

#     def validate_details_data(self, value):
#         # `details_data` wird für Validierung von POST-Daten verwendet
#         if not value:
#             raise serializers.ValidationError("Details data are required and cannot be empty.")

#         if len(value) != 3:
#             raise serializers.ValidationError("Exactly three offer details are required.")

#         offer_types = {detail['offer_type'] for detail in value}
#         if offer_types != {"basic", "standard", "premium"}:
#             raise serializers.ValidationError("Offer details must include exactly one 'basic', one 'standard', and one 'premium' offer type.")

#         return value

#     def create(self, validated_data):

#         details_data = validated_data.pop('details_data', [])
#         offer = Offer.objects.create(**validated_data)

#         for detail_data in details_data:
#             OfferDetail.objects.create(offer=offer, **detail_data)

#         return offer


class OfferSerializer(serializers.ModelSerializer):

    # Für GET, gibt nur id und url zurück
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]
        extra_kwargs = {
            'user': {'read_only': True}  # Macht das 'user'-Feld nur lesbar
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamisch anpassen, basierend auf der HTTP-Methode (POST oder GET)
        if self.context.get('request') and self.context['request'].method == 'POST':
            # Für POST: `details` wird als write_only mit `OfferDetailSerializer` verwendet
            self.fields['details'] = OfferDetailSerializer(
                many=True, write_only=True)
        elif self.context.get('request') and self.context['request'].method == 'GET':
            # Für GET: `details` wird als read_only mit `OfferDetailLinkSerializer` verwendet
            self.fields['details'] = OfferDetailLinkSerializer(
                many=True, read_only=True)

    def get_min_price(self, obj):
        # Berechnet den minimalen Preis der OfferDetails
        return obj.details.aggregate(min_price=Min('price'))['min_price']

    def get_min_delivery_time(self, obj):
        # Berechnet die minimale Lieferzeit der OfferDetails
        return obj.details.aggregate(min_delivery_time=Min('delivery_time_in_days'))['min_delivery_time']

    def create(self, validated_data):
        # Extrahiert `details_data` und erstellt das Offer mit den zugehörigen OfferDetail-Objekten
        details_data = validated_data.pop('details', [])
          # Hole den angemeldeten Benutzer aus dem Kontext
        user = self.context['request'].user if self.context['request'] else None

        # Überprüfe, ob ein Benutzer authentifiziert ist
        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Der Benutzer muss angemeldet sein, um ein Angebot zu erstellen.")

        
        # user = user.user.pk
        offer = Offer.objects.create(user=user, **validated_data)

        # Erstellt die OfferDetail-Objekte und verknüpft sie mit dem Offer
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer


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
