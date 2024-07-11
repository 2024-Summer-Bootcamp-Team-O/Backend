import redis
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from .tasks import get_gpt_answer, get_gpt_result, get_gpt_message
from gpt.serializers import GetGPTMessageSerializer, GetGPTAnswerSerializer

talk_count = 1


class GetGPTMessageView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        request_body=GetGPTMessageSerializer,
        operation_id='GPT의 대사를 가져오는 API',
    )
    def post(self, request):
        global talk_count
        serializer = GetGPTMessageSerializer(data=request.data)
        if serializer.is_valid():
            character_id = serializer.validated_data.get('character_id')
            episode_id = serializer.validated_data.get('episode_id')
            redis_key = "count"

            r = redis.Redis(host='redis', port=6379, db=0)
            if r.exists('episode_id'):
                r.delete('episode_id')
            r.set('episode_id', episode_id)
            r.set(redis_key, talk_count)
            r.set('character_id', character_id)
            talk_count += 1
            result = get_gpt_message.delay(character_id, episode_id)
            return JsonResponse({'task_id': result.task_id}, status=status.HTTP_202_ACCEPTED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetGPTAnswerView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        request_body=GetGPTAnswerSerializer,
        operation_id='GPT의 대답을 가져오는 API',
    )
    def post(self, request):
        serializer = GetGPTAnswerSerializer(data=request.data)
        r = redis.Redis(host='redis', port=6379, db=0)
        if serializer.is_valid():
            choice_content = serializer.validated_data.get('choice_content')
            mz_percent = serializer.validated_data.get('mz_percent')
            character_id = r.get('character_id')
            episode_id = r.get('episode_id')
            talk_content = r.get('talk_content').decode('utf-8')

            result = get_gpt_answer.delay(choice_content, character_id, episode_id, talk_content, mz_percent)

            return JsonResponse({'task_id': result.task_id}, status=status.HTTP_202_ACCEPTED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class GetGPTResultView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_id='GPT의 최종 피드백을 가져오는 API',
    )
    def get(self, request):
        result = get_gpt_result()
        return JsonResponse(result, status=status.HTTP_200_OK)
