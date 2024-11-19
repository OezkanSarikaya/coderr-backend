# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from coderr_app.models import Offer, OfferDetail, User
# from rest_framework.test import APIClient
# from rest_framework import status


# class OfferAPITests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(username='business_user', password='password123')
#         self.business_profile = self.user.profile
#         self.business_profile.type = 'business'
#         self.business_profile.save()

#         self.other_user = User.objects.create_user(username='other_user', password='password123')

#         self.offer = Offer.objects.create(user=self.user, title="Test Offer", description="Test Description")
#         self.detail1 = OfferDetail.objects.create(
#             offer=self.offer,
#             title="Basic Design",
#             revisions=2,
#             delivery_time_in_days=5,
#             price=100.00,
#             features=["Logo Design"],
#             offer_type="basic"
#         )
#         self.detail2 = OfferDetail.objects.create(
#             offer=self.offer,
#             title="Standard Design",
#             revisions=3,
#             delivery_time_in_days=7,
#             price=200.00,
#             features=["Logo Design", "Visitenkarte"],
#             offer_type="standard"
#         )
#         self.detail3 = OfferDetail.objects.create(
#             offer=self.offer,
#             title="Premium Design",
#             revisions=5,
#             delivery_time_in_days=10,
#             price=500.00,
#             features=["Logo Design", "Visitenkarte", "Briefpapier"],
#             offer_type="premium"
#         )

#     def test_get_offers(self):
#         """Test GET /offers/ is accessible to all users and returns paginated results."""
#         response = self.client.get('/offers/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('results', response.data)

#     def test_post_offer_requires_business_user(self):
#         """Test only authenticated business users can POST /offers/"""
#         self.client.login(username='other_user', password='password123')
#         payload = {
#             "title": "New Offer",
#             "description": "A new description",
#             "details": [
#                 {"title": "Basic", "revisions": 2, "delivery_time_in_days": 3, "price": 50, "features": ["Logo"], "offer_type": "basic"},
#                 {"title": "Standard", "revisions": 3, "delivery_time_in_days": 5, "price": 100, "features": ["Logo", "Flyer"], "offer_type": "standard"},
#                 {"title": "Premium", "revisions": 5, "delivery_time_in_days": 7, "price": 200, "features": ["Logo", "Flyer", "Banner"], "offer_type": "premium"}
#             ]
#         }
#         response = self.client.post('/offers/', payload, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#         self.client.logout()
#         self.client.login(username='business_user', password='password123')
#         response = self.client.post('/offers/', payload, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_get_offer_detail(self):
#         """Test GET /offers/{id}/ returns offer details."""
#         response = self.client.get(f'/offers/{self.offer.id}/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['id'], self.offer.id)

#     def test_delete_offer_requires_owner(self):
#         """Test DELETE /offers/{id}/ is only accessible to the offer owner or admin."""
#         self.client.login(username='other_user', password='password123')
#         response = self.client.delete(f'/offers/{self.offer.id}/')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#         self.client.logout()
#         self.client.login(username='business_user', password='password123')
#         response = self.client.delete(f'/offers/{self.offer.id}/')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_patch_offer(self):
#         """Test PATCH /offers/{id}/ updates specified fields."""
#         self.client.login(username='business_user', password='password123')
#         payload = {"title": "Updated Offer"}
#         response = self.client.patch(f'/offers/{self.offer.id}/', payload, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.offer.refresh_from_db()
#         self.assertEqual(self.offer.title, "Updated Offer")

# class OfferAPITests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(username='business_user', password='password123')
#         self.business_profile = self.user.profile
#         self.business_profile.type = 'business'
#         self.business_profile.save()

#         self.other_user = User.objects.create_user(username='other_user', password='password123')

#         self.offer = Offer.objects.create(user=self.user, title="Test Offer", description="Test Description")
#         self.detail1 = OfferDetail.objects.create(
#             offer=self.offer,
#             title="Basic Design",
#             revisions=2,
#             delivery_time_in_days=5,
#             price=100.00,
#             features=["Logo Design"],
#             offer_type="basic"
#         )
#         self.detail2 = OfferDetail.objects.create(
#             offer=self.offer,
#             title="Standard Design",
#             revisions=3,
#             delivery_time_in_days=7,
#             price=200.00,
#             features=["Logo Design", "Visitenkarte"],
#             offer_type="standard"
#         )
#         self.detail3 = OfferDetail.objects.create(
#             offer=self.offer,
#             title="Premium Design",
#             revisions=5,
#             delivery_time_in_days=10,
#             price=500.00,
#             features=["Logo Design", "Visitenkarte", "Briefpapier"],
#             offer_type="premium"
#         )

#     def test_get_offers(self):
#         """Test GET /offers/ is accessible to all users and returns paginated results."""
#         response = self.client.get('/offers/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('results', response.data)

#     def test_post_offer_requires_business_user(self):
#         """Test only authenticated business users can POST /offers/"""
#         self.client.login(username='other_user', password='password123')
#         payload = {
#             "title": "New Offer",
#             "description": "A new description",
#             "details": [
#                 {"title": "Basic", "revisions": 2, "delivery_time_in_days": 3, "price": 50, "features": ["Logo"], "offer_type": "basic"},
#                 {"title": "Standard", "revisions": 3, "delivery_time_in_days": 5, "price": 100, "features": ["Logo", "Flyer"], "offer_type": "standard"},
#                 {"title": "Premium", "revisions": 5, "delivery_time_in_days": 7, "price": 200, "features": ["Logo", "Flyer", "Banner"], "offer_type": "premium"}
#             ]
#         }
#         response = self.client.post('/offers/', payload, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#         self.client.logout()
#         self.client.login(username='business_user', password='password123')
#         response = self.client.post('/offers/', payload, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_get_offer_detail(self):
#         """Test GET /offers/{id}/ returns offer details."""
#         response = self.client.get(f'/offers/{self.offer.id}/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['id'], self.offer.id)

#     def test_delete_offer_requires_owner(self):
#         """Test DELETE /offers/{id}/ is only accessible to the offer owner or admin."""
#         self.client.login(username='other_user', password='password123')
#         response = self.client.delete(f'/offers/{self.offer.id}/')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#         self.client.logout()
#         self.client.login(username='business_user', password='password123')
#         response = self.client.delete(f'/offers/{self.offer.id}/')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_patch_offer(self):
#         """Test PATCH /offers/{id}/ updates specified fields."""
#         self.client.login(username='business_user', password='password123')
#         payload = {"title": "Updated Offer"}
#         response = self.client.patch(f'/offers/{self.offer.id}/', payload, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.offer.refresh_from_db()
#         self.assertEqual(self.offer.title, "Updated Offer")



