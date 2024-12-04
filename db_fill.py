
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coderr_project.settings')
django.setup()

from django.contrib.auth.models import User
from coderr_app.models import Profile, Offer, OfferDetail, Order, Review
from django.db import transaction
import random
from rest_framework.authtoken.models import Token

def create_users():
    """Erstellt Beispiel-Benutzer mit Profilen."""
    business_users = []
    customer_users = []

    user = User.objects.create_user(
            username=f'Anbieter',
            first_name='Michael',
            last_name='Schmidt',
            email=f'michael@example.com',
            password='123456'
        )
    
    Profile.objects.create(
            user=user,
            type='business',
            description=f'Ich bin ein Fullstack Developer. Mein Main-Stack ist Angular und Django',
            email=user.email
        )
    
    business_users.append(user)
    # Token explizit erstellen
    Token.objects.get_or_create(user=user)
    
    user = User.objects.create_user(
            username=f'Kunde',
            first_name='Maria',
            last_name='Müller',
            email=f'maria@example.com',
            password='123456'
        )
    
    Profile.objects.create(
            user=user,
            type='customer',            
            email=user.email
        )
    
    customer_users.append(user)
    Token.objects.get_or_create(user=user)

    for i in range(3):  # 3 Business-Benutzer
        user = User.objects.create_user(
            username=f'business_user{i + 1}',
            first_name='Business',
            last_name=f'User{i + 1}',
            email=f'business{i + 1}@example.com',
            password='password123'
        )
        Profile.objects.create(
            user=user,
            type='business',
            description=f'Business User {i + 1} Beschreibung',
            email=user.email
        )
        business_users.append(user)
        Token.objects.get_or_create(user=user)

    for i in range(3):  # 3 Kunden-Benutzer
        user = User.objects.create_user(
            username=f'customer_user{i + 1}',
            first_name='Customer',
            last_name=f'User{i + 1}',
            email=f'customer{i + 1}@example.com',
            password='password123'
        )
        Profile.objects.create(
            user=user,
            type='customer',
            description=f'Customer User {i + 1} Beschreibung',
            email=user.email
        )
        customer_users.append(user)
        Token.objects.get_or_create(user=user)

    return business_users, customer_users


def create_offers_and_details(business_users):
    """Erstellt Angebote und deren Details für Business-Benutzer."""
    offers = []

    for business_user in business_users:
        for i in range(2):  # Jeder Business-Benutzer hat 2 Angebote
            offer = Offer.objects.create(
                user=business_user,
                title=f"Angebot {i + 1} von {business_user.username}",
                description=f"Dies ist das Angebot {i + 1} von {business_user.username}."
            )
            offers.append(offer)

            # Erstelle Details für jedes Angebot
            for j, offer_type in enumerate(['basic', 'standard', 'premium']):
                OfferDetail.objects.create(
                    offer=offer,
                    title=f"{offer.title} - {offer_type.capitalize()}",
                    revisions=j + 1,
                    delivery_time_in_days=random.randint(1, 10),
                    price=random.uniform(50, 500),
                    features=["Startseite", "Angebote"],  # Korrekte Liste von Features
                    offer_type=offer_type
                )
    return offers


def create_orders(customer_users, offers):
    """Erstellt Bestellungen für Kunden und Business-Benutzer."""
    orders = []

    for i, customer_user in enumerate(customer_users):
        # Zufällige Angebote auswählen
        offer = random.choice(offers)
        business_user = offer.user

        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            title=f"Bestellung für {offer.title}",
            revisions=1,
            delivery_time_in_days=random.randint(3, 10),
            price=random.uniform(100, 1000),
            features=["Feature1", "Feature2", "Feature3"],  # Korrekte Liste von Features
            offer_type=random.choice(['basic', 'standard', 'premium']),
            status=random.choice(['in_progress', 'completed', 'cancelled'])
        )
        orders.append(order)
    return orders


def create_reviews(customer_users, business_users):
    """Erstellt Bewertungen zwischen Kunden und Business-Benutzern."""
    for customer_user in customer_users:
        for business_user in business_users:
            Review.objects.create(
                business_user=business_user,
                reviewer=customer_user,
                rating=random.randint(1, 5),
                description=f"Review von {customer_user.username} für {business_user.username}."
            )


@transaction.atomic
def populate_database():
    """Füllt die Datenbank mit Beispieldaten."""
    print("Erstelle Benutzer und Profile...")
    business_users, customer_users = create_users()

    print("Erstelle Angebote und deren Details...")
    offers = create_offers_and_details(business_users)

    print("Erstelle Bestellungen...")
    create_orders(customer_users, offers)

    print("Erstelle Bewertungen...")
    create_reviews(customer_users, business_users)

    print("Datenbank erfolgreich gefüllt!")


# Skript ausführen
if __name__ == '__main__':
    populate_database()
