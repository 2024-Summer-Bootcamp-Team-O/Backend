from rest_framework import serializers
from .models import chat_room,character,user

class ChatRoomSerializer(serializers.ModelSerializer):
    character_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = chat_room
        fields = ['user_id','character_id']
    def create(self, validated_data):
        character_id = validated_data.pop('character_id')
        user_id = validated_data.pop('user_id')
        character_instance = character.objects.get(character_id=character_id)
        user_instance = user.objects.get(id =user_id)
        chat_room_instance = chat_room.objects.create(character=character_instance, user=user_instance, **validated_data)
        return chat_room_instance


class AnswerSerializer(serializers.Serializer):
    choice_content = serializers.CharField(max_length=1000)
    mz_percent = serializers.IntegerField()
