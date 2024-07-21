import requests
import redis
import boto3

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from django.db.models.functions import Random
from rest_framework_simplejwt.authentication import JWTAuthentication

from rumz import settings
from .models import episode, chat_episode, chat_room, photo
from .serializers import ChatRoomSerializer, UploadPhotoSerializer

r = redis.Redis(host="redis", port=6379, db=0)


class CreateChatRoomView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChatRoomSerializer,
        operation_id="대화시작 시 캐릭터 정보를 저장하고 상황을 랜덤 배정하는 API",
    )
    def post(self, request, *args, **kwargs):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.user.id
            character_id = serializer.validated_data.get("character_id")
            chat_room_instance = chat_room.objects.create(
                user_id=user_id, character_id=character_id
            )
            chat_room_instance.save()
            r.set("room_id", chat_room_instance.id)
            # 저장된 데이터에서 character_id 추출
            character_id = chat_room_instance.character_id
            r.set("character_id", character_id)
            next_episode_time_id = get_next_episode_time_id(0)
            next_episode_id = get_random_episode_id(next_episode_time_id)
            response = get_gpt_message(request, character_id, next_episode_id)
            if response.status_code == status.HTTP_202_ACCEPTED:
                return JsonResponse(
                    {
                        "character_id": character_id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return JsonResponse(response.json(), status=response.status_code)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NextEpisodeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="다음 상황을 랜덤 제공하는 API",
    )
    def get(self, request):
        character_id = r.get("character_id").decode("utf-8")
        room_id = int(r.get("room_id"))
        count = int(r.get("count"))
        next_episode_time_id = get_next_episode_time_id(count)
        next_episode_id = get_random_episode_id(next_episode_time_id)

        chat_room_instance = chat_room.objects.get(id=room_id)
        episode_instance = episode.objects.get(id=next_episode_id)

        chat_episode_instance = chat_episode(
            chat_room=chat_room_instance, episode=episode_instance
        )
        chat_episode_instance.save()
        r.delete("conversation_history")
        response = get_gpt_message(request, character_id, next_episode_id)
        if response.status_code == status.HTTP_202_ACCEPTED:
            return JsonResponse(
                {
                    "character_id": character_id,
                },
                status=status.HTTP_201_CREATED,
            )
        return JsonResponse(response.json(), status=response.status_code)


class GetFeedbackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="GPT의 피드백을 가져오는 API",
    )
    def get(self, request):
        response = get_gpt_feedback(request)
        if response.status_code == status.HTTP_202_ACCEPTED:
            return Response(
                "피드백이 생성되었습니다.",
                status=status.HTTP_201_CREATED,
            )


class ResultChatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_id="대화 종료 시 피드백을 출력하고 저장하는 API")
    def get(self, request):
        room_id = r.get("room_id")

        if room_id is None:
            return JsonResponse(
                {"error": "room_id not found in Redis"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room_id = int(room_id)

        # GPT 결과 요청
        result_response = get_gpt_result(request)
        photo_instance = photo.objects.get(chat_room_id=room_id)
        photo_url = photo_instance.image_url

        result_data = result_response.json()

        # 데이터베이스에 피드백 저장
        chat_room_instance = chat_room.objects.get(id=room_id)
        chat_room_instance.result = result_data.get("result", "")
        chat_room_instance.save()
        r.flushall()
        return JsonResponse(
            {
                "result": result_data.get("result", ""),
                "image_url": photo_url,
                "name": request.user.name
            },
            status=status.HTTP_200_OK,
        )


class PhotoUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_id="사진을 업로드하는 API",
        request_body=UploadPhotoSerializer,
    )
    def post(self, request):
        serializer = UploadPhotoSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data["image"]
            file_url = upload_to_s3(image)
            photo_instance = photo.objects.create(
                image_url=file_url,
                chat_room_id=r.get("room_id").decode("utf-8"),
            )
            photo_instance.save()
            return JsonResponse(
                {"message": "사진이 업로드 되었습니다.", "url": file_url},
                status=status.HTTP_200_OK,
            )
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def upload_to_s3(file):
    # setting 파일에서 가져옴
    custom_domain = settings.AWS_CLOUDFRONT_DOMAIN
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    file_id = r.get("room_id").decode("utf-8")
    file_path = f"image/{file_id}"
    s3_client.upload_fileobj(
        file,
        bucket_name,
        file_path,
        ExtraArgs={
            "CacheControl": settings.AWS_S3_OBJECT_PARAMETERS["CacheControl"],
            "ContentType": file.content_type,
        },
    )
    file_url = f"https://{custom_domain}/{file_path}"
    return file_url


def get_gpt_result(request):
    url = f"http://0.0.0.0:8000/gpts/results"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_jwt_token(request)}",
    }
    return requests.get(url, headers=headers)


def get_next_episode_time_id(count):
    return count + 1


def get_gpt_message(request, character_id, episode_id):
    url = f"http://0.0.0.0:8000/gpts/messages"
    payload = {"character_id": character_id, "episode_id": episode_id}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_jwt_token(request)}",
    }
    return requests.post(url, json=payload, headers=headers)


def get_gpt_answer(request, choice_content):
    url = f"http://0.0.0.0:8000/gpts/answers"
    payload = {"choice_content": choice_content}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_jwt_token(request)}",
    }
    return requests.post(url, json=payload, headers=headers)


def get_gpt_feedback(request):
    url = f"http://0.0.0.0:8000/gpts/feedbacks"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_jwt_token(request)}",
    }
    return requests.get(url, headers=headers)


def get_random_episode_id(episode_time_id):
    random_episode = (
        episode.objects.filter(episode_flow_id=episode_time_id)
        .order_by(Random())
        .first()
    )
    if random_episode is None:
        return None
    return random_episode.id


def get_jwt_token(request):
    return request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
