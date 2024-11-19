from django.test import TestCase
from django.contrib.auth import get_user_model
from coderr_app.models import Offer, OfferDetail, Profile
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class OfferAndOfferDetailModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='business_user', password='password123')
        self.business_profile = self.user.profile
        self.business_profile.type = 'business'
        self.business_profile.save()

    def test_create_offer_and_offer_details(self):
        """Test creating an Offer with associated OfferDetails"""
        offer = Offer.objects.create(user=self.user, title="Design Offer", description="A great offer")
        detail1 = OfferDetail.objects.create(
            offer=offer,
            title="Basic Design",
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=["Logo Design", "Visitenkarte"],
            offer_type="basic"
        )
        detail2 = OfferDetail.objects.create(
            offer=offer,
            title="Standard Design",
            revisions=5,
            delivery_time_in_days=7,
            price=200.00,
            features=["Logo Design", "Visitenkarte", "Briefpapier"],
            offer_type="standard"
        )
        detail3 = OfferDetail.objects.create(
            offer=offer,
            title="Premium Design",
            revisions=10,
            delivery_time_in_days=10,
            price=500.00,
            features=["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
            offer_type="premium"
        )
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)
        self.assertEqual(detail1.offer, offer)
        self.assertEqual(detail2.offer, offer)
        self.assertEqual(detail3.offer, offer)
