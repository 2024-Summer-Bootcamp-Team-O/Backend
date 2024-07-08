from rest_framework import serializers


class GetGPTTalkSerializer(serializers.Serializer):
    character_id = serializers.IntegerField()
    episode_id = serializers.IntegerField()


class GetGPTAnswerSerializer(serializers.Serializer):
    choice_content = serializers.CharField(max_length=1000)
    character_id = serializers.IntegerField()


class GetGPTChoiceSerializer(serializers.Serializer):
    talk_content = serializers.CharField(max_length=1000)


class GetGPTFeedbackSerializer(serializers.Serializer):
    choice_content = serializers.CharField(max_length=1000)
    mz_percent = serializers.IntegerField()
