import redis
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .tasks import get_gpt_result, get_gpt_message, get_gpt_feedback
from gpt.serializers import GetGPTMessageSerializer


class GetGPTMessageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=GetGPTMessageSerializer,
        operation_id="GPT의 대사를 가져오는 API",
    )
    def post(self, request):
        serializer = GetGPTMessageSerializer(data=request.data)
        if serializer.is_valid():
            character_id = serializer.validated_data.get("character_id")
            episode_id = serializer.validated_data.get("episode_id")

            r = redis.Redis(host="redis", port=6379, db=0)
            if r.exists("episode_id"):
                r.delete("episode_id")
            r.set("episode_id", episode_id)
            if r.exists("count"):
                r.incr("count")
            else:
                r.set("count", 1)
            r.set("character_id", character_id)
            result = get_gpt_message.delay(character_id, episode_id)
            return JsonResponse(
                {"task_id": result.task_id}, status=status.HTTP_202_ACCEPTED
            )
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetGPTFeedbackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="GPT의 피드백을 가져오는 API",
    )
    def get(self, request):
        result = get_gpt_feedback.delay()
        return JsonResponse(
            {"task_id": result.task_id}, status=status.HTTP_202_ACCEPTED
        )


class GetGPTResultView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="GPT의 최종 피드백을 가져오는 API",
    )
    def get(self, request):
        reponse = get_gpt_result()
        result = {"result": reponse}
        return JsonResponse(result, status=status.HTTP_200_OK)
