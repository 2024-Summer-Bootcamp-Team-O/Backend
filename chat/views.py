import redis
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from .serializers import GetGPTTalkSerializer, GetGPTAnswerSerializer, GetGPTChoiceSerializer, GetGPTFeedbackSerializer
from .tasks import get_gpt_talk, get_gpt_answer, get_gpt_choice

choice_count = 1


class GetGPTTalkView(APIView):
    @swagger_auto_schema(
        request_body=GetGPTTalkSerializer,
        operation_id='GPT의 대사를 가져오는 API',
    )
    def post(self, request):
        serializer = GetGPTTalkSerializer(data=request.data)
        if serializer.is_valid():
            character_id = serializer.validated_data.get('character_id')
            episode_id = serializer.validated_data.get('episode_id')

            result = get_gpt_talk.delay(character_id, episode_id)
            return JsonResponse({'task_id': result.task_id}, status=status.HTTP_202_ACCEPTED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetGPTAnswerView(APIView):
    @swagger_auto_schema(
        request_body=GetGPTAnswerSerializer,
        operation_id='GPT의 대답을 가져오는 API',
    )
    def post(self, request):
        serializer = GetGPTAnswerSerializer(data=request.data)
        if serializer.is_valid():
            choice_content = serializer.validated_data.get('choice_content')
            character_id = serializer.validated_data.get('character_id')

            result = get_gpt_answer.delay(choice_content, character_id)
            return JsonResponse({'task_id': result.task_id}, status=status.HTTP_202_ACCEPTED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetGPTChoiceView(APIView):
    @swagger_auto_schema(
        request_body=GetGPTChoiceSerializer,
        operation_id='GPT의 선택지를 가져오는 API',
    )
    def post(self, request):
        serializer = GetGPTChoiceSerializer(data=request.data)
        if serializer.is_valid():
            talk_content = serializer.validated_data.get('talk_content')

            result = get_gpt_choice.delay(talk_content)
            return JsonResponse({'task_id': result.task_id}, status=status.HTTP_202_ACCEPTED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
