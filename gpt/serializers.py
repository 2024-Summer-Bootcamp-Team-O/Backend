from rest_framework import serializers


class GetGPTMessageSerializer(serializers.Serializer):
    character_id = serializers.IntegerField()
    episode_id = serializers.IntegerField()
