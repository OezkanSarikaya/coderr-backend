from rest_framework import serializers
from coderr_app.models import Profile
from django.contrib.auth.models import User
from django.conf import settings  # Für Zugriff auf MEDIA_URL

class UserPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk','first_name', 'last_name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name', 'last_name'] 

class ProfileSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    file = serializers.FileField(required=False)
    class Meta:
        model = Profile
        # fields = '__all__'
        fields = ['user', 'file','location', 'tel', 'description', 'working_hours','type', 'email', 'created_at']
        extra_kwargs = {
            'file': {'required': False}  # Das Feld `file` ist nicht erforderlich
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Überprüfen, ob das Feld `file` einen Wert hat und füge nur den relativen Pfad hinzu
        if instance.file:
            # MEDIA_URL direkt verwenden, um doppelte URLs zu vermeiden
            representation['file'] = f"{settings.MEDIA_URL}{instance.file}"
        
        return representation

    # def get_file(self, obj):
    #     # Nur den relativen Pfad (ohne Domain) zurückgeben
    #     if obj.file and hasattr(obj.file, 'url'):
    #         return obj.file.url.lstrip('/')
    #     return None
    
    # def update(self, instance, validated_data):
    #     # Wenn Benutzerdaten vorhanden sind, aktualisiere sie
    #     user_data = validated_data.pop('user', None)
    #     if user_data:
    #         user_instance = instance.user
    #         user_instance.first_name = user_data.get('first_name', user_instance.first_name)
    #         user_instance.last_name = user_data.get('last_name', user_instance.last_name)
    #         user_instance.save()

    #     # Aktualisiere die anderen Felder des Profil-Objekts
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance