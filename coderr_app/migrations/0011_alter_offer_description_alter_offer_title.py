# Generated by Django 5.1.3 on 2024-12-05 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coderr_app', '0010_alter_review_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='description',
            field=models.TextField(default='defaultdescription', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='offer',
            name='title',
            field=models.CharField(default='defaulttitel', max_length=255),
            preserve_default=False,
        ),
    ]
