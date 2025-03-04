# Generated by Django 5.1.3 on 2024-11-21 13:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coderr_app', '0009_alter_profile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Bewertung muss mindestens einen Stern haben.'), django.core.validators.MaxValueValidator(5, message='Bewertung darf 5 Sterne nicht überschreiten!')]),
        ),
    ]
