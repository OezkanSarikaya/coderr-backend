from rest_framework import serializers
from coderr_app.models import Profile
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        # fields = ['id', 'content', 'author', 'created_at']