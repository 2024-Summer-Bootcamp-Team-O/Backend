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
        user_email = request.user.email
        serializer = GetGPTMessageSerializer(data=request.data)
        if serializer.is_valid():
            character_id = serializer.validated_data.get("character_id")
            episode_id = serializer.validated_data.get("episode_id")

            r = redis.Redis(host="redis", port=6379, db=0)
            if r.exists(f"episode_id:{user_email}"):
                r.delete(f"episode_id:{user_email}")
            r.set(f"episode_id:{user_email}", episode_id)
            if r.exists(f"count:{user_email}"):
                r.incr(f"count:{user_email}")
            else:
                r.set(f"count:{user_email}", 1)
            r.set(f"character_id:{user_email}", character_id)
            result = get_gpt_message.delay(character_id, episode_id, user_email)
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
        user_email = request.user.id
        result = get_gpt_feedback.delay(user_email)
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
        user_email = request.user.id
        reponse = get_gpt_result(user_email)
        result = {"result": reponse}
        return JsonResponse(result, status=status.HTTP_200_OK)
