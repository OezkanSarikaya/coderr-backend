# Generated by Django 5.1.3 on 2024-11-20 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coderr_app', '0008_alter_offer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='profile_images/'),
        ),
    ]
