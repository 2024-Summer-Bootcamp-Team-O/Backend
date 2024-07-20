from rest_framework import serializers
from .models import chat_room, photo


class ChatRoomSerializer(serializers.ModelSerializer):
    character_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = chat_room
        fields = ["character_id"]


class UploadPhotoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = photo
        fields = ["image"]
