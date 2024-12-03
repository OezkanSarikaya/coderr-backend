from rest_framework import serializers
from coderr_app.models import Profile, Offer, Order, OfferDetail, Review
from django.contrib.auth.models import User
from django.conf import settings  # For access to MEDIA_URL
from django.urls import reverse
from django.db.models import Min
from rest_framework.exceptions import ValidationError


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """
    Creates Link for single or list view of each detail
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

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
            raise serializers.ValidationError("Der Benutzer muss angemeldet sein.")

        # Only `customer_user` are allowed to create an order
        if request.method == 'POST':
            if not hasattr(request.user, 'profile') or request.user.profile.type != 'customer':
                raise serializers.ValidationError(
                    "Nur Benutzer mit Kundenprofil können Bestellungen erstellen."
                )

        # Only `business_user` are allowed to update an order
        if request.method in ['PUT', 'PATCH']:
            order = self.instance
            if not (request.user == order.business_user):
                raise serializers.ValidationError(
                    "Sie haben keine Berechtigung diese Bestellung zu bearbeiten"
                )

        return attrs

    def create(self, validated_data):
        """
        Create a new order, only allowed for customer users.
        """
        request = self.context.get('request')
        customer_user = request.user
        offer_detail_id = validated_data.pop('offer_detail_id', None)

        # Ensure the OfferDetail exists
        offer_detail = OfferDetail.objects.get(id=offer_detail_id)

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
        # Revisions must not be below -1
        if data['revisions'] < -1:
            raise serializers.ValidationError(
                "Revisions must be -1 or greater.")

        # The delivery time must be positive
        if data['delivery_time_in_days'] <= 0:
            raise serializers.ValidationError(
                "Delivery time must be a positive integer.")

        # Features must have at least one entry
        if not data['features']:
            raise serializers.ValidationError(
                "Mindestens ein Feature muss angegeben werden.")

        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Define fields for user
    """
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

        # Add the relative path for the `file` field, if available
        if instance.file:
            representation['file'] = f"{settings.MEDIA_URL}{instance.file}"

        return representation


class OfferSerializer(serializers.ModelSerializer):
    """
    Offer serializer for both creating and fetching offers.
    """
    details = serializers.SerializerMethodField()
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
            'user': {'read_only': True}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.fields['details'] = OfferDetailSerializer(many=True, write_only=False)
        elif request and request.method == 'GET':
            self.fields['details'] = OfferDetailLinkSerializer(many=True, read_only=True)

    def get_details(self, obj):
        # Returns details for the response based on the request context
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            return OfferDetailSerializer(obj.details.all(), many=True).data
        return OfferDetailLinkSerializer(obj.details.all(), many=True).data

    def get_min_price(self, obj):
        return obj.details.aggregate(min_price=Min('price'))['min_price']

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(min_delivery_time=Min('delivery_time_in_days'))['min_delivery_time']



    def create(self, validated_data):
        """
        Create an Offer and its associated OfferDetails with validation for three required details.
        """
        details_data = validated_data.pop('details', [])
        user = self.context['request'].user

        # Ensure `user` isn't passed twice
        if 'user' in validated_data:
            del validated_data['user']

        errors = {}

        # Validate the number of details
        if len(details_data) != 3:
            errors['details'] = ["Es müssen genau 3 Angebotsdetails übergeben werden."]
        
        # Validate the offer_types
        required_offer_types = {'basic', 'standard', 'premium'}
        offer_types = {detail['offer_type'] for detail in details_data}
        if offer_types != required_offer_types:
            errors['details'] = errors.get('details', []) + [
                "Die Angebotsdetails müssen genau eines der folgenden offer_type beinhalten: 'basic', 'standard' und 'premium'."
            ]

        if errors:
            raise ValidationError(errors)

        # Create the offer
        offer = Offer.objects.create(user=user, **validated_data)

        # Create associated OfferDetails
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer
    
    def update(self, instance, validated_data):
        # Aktualisieren der Felder des Offer
        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Verarbeite die verschachtelten 'details' Daten
        details_data = validated_data.get('details', [])

        # Lösche die alten Details (optional, je nachdem, wie du es handhaben möchtest)
        instance.details.all().delete()

        # Erstelle die neuen Details
        for detail_data in details_data:
            OfferDetail.objects.create(offer=instance, **detail_data)

        return instance





class ProfileSerializer(serializers.ModelSerializer):
    """
    Defines fields for profile and include nested user data
    """
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
