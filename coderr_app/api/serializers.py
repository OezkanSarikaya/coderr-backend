from rest_framework import serializers
from coderr_app.models import Profile, Offer, Order, OfferDetail, Review
from django.contrib.auth.models import User
from django.conf import settings  # For access to MEDIA_URL
from django.urls import reverse
from django.db.models import Min
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.db.models import Min
from django.db import models
from django.utils.html import strip_tags


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """
    Creates Link for single or list view of each detail
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url', 'title']

    def get_url(self, obj):
        # Dynamically create the URL path for each OfferDetail object
        return reverse('offerdetails-detail', args=[obj.id])


class ReviewSerializer(serializers.ModelSerializer):
    """
    Validates reviews and rating
    """
    reviewer = serializers.ReadOnlyField(source='reviewer.id')

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Ensure a user can only leave one review per business user.
        """
        # Use context to access the authenticated user
        business_user = data.get('business_user')
        reviewer = self.context['request'].user

        if Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            raise serializers.ValidationError(
                "You can only leave one review per business user.")

        return data

    def validate_rating(self, value):
        """
        Ensure the rating is between 1 and 5.
        """
        if not (1 <= value <= 5):
            raise serializers.ValidationError(
                "Rating must be between 1 and 5.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """
    Validates orders and check permissions
    """
    offer_detail_id = serializers.IntegerField(
        write_only=True, required=False  # `offer_detail_id` only needed for create
    )
    # Custom field to ensure price is output as a number (decimal, not string)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, read_only=True)


    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at', 'offer_detail_id'
        ]
        read_only_fields = [
            'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type'
        ]

    def validate(self, attrs):
        """
        Validates user permissions based on the request type (create or update).
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError({"detail": ["Der Benutzer muss angemeldet sein."]}, code=status.HTTP_401_UNAUTHORIZED)

        # Only `customer_user` are allowed to create an order
        if request.method == 'POST':
            if not hasattr(request.user, 'profile') or request.user.profile.type != 'customer':
                raise serializers.ValidationError({"detail": ["Nur Benutzer mit Kundenprofil können Bestellungen erstellen"]}, code=status.HTTP_403_FORBIDDEN)

        # Only `business_user` are allowed to update an order
        if request.method in ['PUT', 'PATCH']:
            order = self.instance
            if not (request.user == order.business_user):
                raise serializers.ValidationError({"detail": ["Sie haben keine Berechtigung diese Bestellung zu bearbeiten"]}, code=status.HTTP_403_FORBIDDEN)

                   
                

        return attrs

    def create(self, validated_data):
        """
        Create a new order, only allowed for customer users.
        """
        request = self.context.get('request')
        customer_user = request.user
        offer_detail_id = validated_data.pop('offer_detail_id', None)

       # Ensure the OfferDetail exists
        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError({"offer_detail_id": ["Angebotsdetail mit dieser ID existiert nicht."]})


        # Create the order
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
    """
    Validates OfferDetails
    """
    offer_type = serializers.ChoiceField(choices=['basic', 'standard', 'premium'])

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type']

    def validate(self, data):
        errors = {}

        # Revisions must not be below -1
        revisions = data.get('revisions')
        if revisions is not None and revisions < -1:
            errors['revisions'] = "Revisions must be -1 or greater."

        # The delivery time must be positive
        delivery_time = data.get('delivery_time_in_days')
        if delivery_time is not None and delivery_time <= 0:
            errors['delivery_time_in_days'] = "Delivery time must be a positive integer."

        # Features must have at least one entry
        features = data.get('features')
        if features is not None and not features:
            errors['features'] = "Mindestens ein Feature muss angegeben werden."

        # Raise ValidationError if there are any errors
        if errors:
            raise serializers.ValidationError(errors)

        return data



class UserSerializer(serializers.ModelSerializer):
    """
    Define fields for user
    """

    def validate_first_name(self, value):
        """Clean HTML tags from first_name."""
        return strip_tags(value)

    def validate_last_name(self, value):
        """Clean HTML tags from last_name."""
        return strip_tags(value)
    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'username']


class BusinessSerializer(serializers.ModelSerializer):
    """
    Define fields for business profiles with nested user data
    """
    user = UserSerializer()  # nested user serializer
    file = serializers.FileField(required=False)

    class Meta:
        model = Profile
        fields = [
            'user',           # nested user object
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
        ]
        extra_kwargs = {
            'file': {'required': False}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Iterate over fields and replace None with an empty string
        for field in representation:
            if representation[field] is None:
                representation[field] = ''

        # Add the relative path for the `file` field, if available
        if instance.file:
            representation['file'] = f"{settings.MEDIA_URL}{instance.file}"

        return representation


class CustomerSerializer(serializers.ModelSerializer):
    """
    Define fields for customer profiles with nested user data
    """
    user = UserSerializer()  # nested user serializer
    file = serializers.FileField(required=False)

    class Meta:
        model = Profile
        fields = [
            'user',           # nested user object
            'file',
            'created_at',
            'type',
        ]
        extra_kwargs = {
            'file': {'required': False}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Rename 'created_at' to 'uploaded_at'
        if 'created_at' in representation:
            representation['uploaded_at'] = representation.pop('created_at')


        # Add the relative path for the `file` field, if available
        if instance.file:
            representation['file'] = f"{settings.MEDIA_URL}{instance.file}"


        return {
            'user': representation['user'],
            'file': representation.get('file', ''),
            'uploaded_at': representation['uploaded_at'],
            'type': representation['type'],
        }
    


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)  # Für POST verwenden wir den vollständigen Detail-Serializer
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_min_price(self, obj):
        min_price = obj.details.aggregate(min_price=Min('price'))['min_price']
        return float(min_price) if min_price is not None else None

    def get_min_delivery_time(self, obj):
        min_delivery_time = obj.details.aggregate(min_delivery_time=Min('delivery_time_in_days'))['min_delivery_time']
        return int(min_delivery_time) if min_delivery_time is not None else None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.fields['details'] = OfferDetailSerializer(many=True)  # Für POST verwenden wir den vollständigen Serializer
        elif request and request.method == 'GET':
            self.fields['details'] = OfferDetailLinkSerializer(many=True, read_only=True)  # Für GET verwenden wir den Link-Serializer



    def create(self, validated_data):
        """
        Erstelle ein Angebot und die zugehörigen Angebotsdetails.
        """
        details_data = validated_data.pop('details', [])

        # Prüfen, ob genau 3 Details vorhanden sind
        if len(details_data) != 3:
            raise serializers.ValidationError({"details": ["Es müssen genau 3 Angebotsdetails übergeben werden."]})

        offer_types = {detail.get('offer_type') for detail in details_data}
        if offer_types != {'basic', 'standard', 'premium'}:
            raise serializers.ValidationError({"details": ["Die 3 Angebotsdetails müssen die Typen 'basic', 'standard' und 'premium' enthalten."]})

        # Erstelle das Angebot
        offer = Offer.objects.create(**validated_data)

        # Erstelle die zugehörigen Angebotsdetails
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer

    def update(self, instance, validated_data):
        """
        Update das bestehende Angebot.
        """
        details_data = validated_data.pop('details', None)

        # Wenn Details im PATCH enthalten sind, dann aktualisieren
        if details_data is not None:
            # Entferne alle bestehenden Details und füge die neuen hinzu
            instance.details.all().delete()
            for detail_data in details_data:
                OfferDetail.objects.create(offer=instance, **detail_data)

        # Aktualisiere die Felder des Angebots
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance






class ProfileSerializer(serializers.ModelSerializer):
    """
    Defines fields for profile and include nested user data
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # ID of user
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    file = serializers.FileField(required=False)

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
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

    def validate_description(self, value):
        """Clean HTML tags from description field."""
        return strip_tags(value)

    def validate_location(self, value):
        """Clean HTML tags from location field."""
        return strip_tags(value)

    def validate_working_hours(self, value):
        """Clean HTML tags from working_hours field."""
        return strip_tags(value)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        user_data = {
            "user": instance.user.id,
            "username": instance.user.username,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name
        }

        representation.update(user_data)
        # Check if the field `file` has a value and add only the relative path
        if instance.file:
            # Use MEDIA_URL directly to avoid duplicate URLs
            representation['file'] = f"{settings.MEDIA_URL}{instance.file}"

        return representation
