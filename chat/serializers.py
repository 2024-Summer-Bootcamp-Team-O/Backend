from rest_framework import serializers


class AnswerSerializer(serializers.Serializer):
    choice_content = serializers.CharField(max_length=1000)
    mz_percent = serializers.IntegerField()
