from rest_framework import serializers


class GetGPTMessageSerializer(serializers.Serializer):
    character_id = serializers.IntegerField()
    episode_id = serializers.IntegerField()


class GetGPTAnswerSerializer(serializers.Serializer):
    choice_content = serializers.CharField(max_length=1000)
    mz_percent = serializers.IntegerField()
