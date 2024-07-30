import redis

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import chat_room, photo
from user.models import user
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserRegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer

r = redis.Redis(host="redis", port=6379, db=0)


class UserRegistrationView(APIView):

    @swagger_auto_schema(
        operation_id="회원가입을 위한 API",
        request_body=UserRegistrationSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"message": "회원가입에 성공하였습니다."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckUserEmailView(APIView):
    @swagger_auto_schema(
        operation_id="이메일 중복 확인 API",
        manual_parameters=[
            openapi.Parameter(
                "email",
                openapi.IN_QUERY,
                description="중복 확인할 이메일",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={200: "사용 가능한 이메일입니다", 409: "이미 존재하는 이메일입니다"},
    )
    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        if user.objects.filter(email=email).exists():
            return Response(
                {"message": "이미 존재하는 이메일입니다"},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"message": "사용 가능한 이메일입니다"}, status=status.HTTP_200_OK
        )


class LoginView(APIView):
    @swagger_auto_schema(
        operation_id="로그인을 위한 API",
        request_body=LoginSerializer,
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(member)
            return Response(
                {
                    "message": "로그인에 성공하였습니다.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_id="로그아웃을 위한 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="리프레시 토큰"
                ),
            },
        ),
        responses={
            200: "로그아웃 성공",
            400: "리프레시 토큰 필요",
        },
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        user_email = request.user.email
        if not refresh_token:
            return Response(
                {"message": "리프레시 토큰이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for key in r.scan_iter(f"*{user_email}*"):
            r.delete(key)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {"message": "로그아웃되었습니다."}, status=status.HTTP_205_RESET_CONTENT
        )


# 결과페이지 조회
class UserResultView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_id="사용자의 대화 결과를 조회하는 API")
    def get(self, request):
        user_id = request.user.id
        photo_chat_room_ids = photo.objects.filter(chat_room__user_id=user_id).values_list('chat_room_id', flat=True)
        chat_rooms = chat_room.objects.filter(
            Q(user_id=user_id) & ~Q(result="") & Q(id__in=photo_chat_room_ids)
        ).select_related('user')

        if chat_rooms.exists():
            response_data = {
                "status": "200",
                "message": "결과 조회 성공",
                "data": [
                    {
                        "room_id": room.id,
                        "character_id": room.character_id,
                        "name": room.user.name,
                        "image_url": photo.objects.get(chat_room_id=room.id).image_url
                    }
                    for room in chat_rooms
                ],
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(
            {
                "status": "200",
                "message": "No chat rooms found for the user",
                "data": [],
            },
            status=status.HTTP_200_OK,
        )


class UserDetailResultView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="결과를 삭제하는 API", responses={200: "삭제 성공"}
    )
    def delete(self, request, room_id):
        try:
            chat_room_instance = chat_room.objects.get(id=room_id)
            chat_room_instance.result = ""
            chat_room_instance.save()
            response_data = {"status": "200", "message": "삭제 성공"}
            return Response(response_data, status=status.HTTP_200_OK)
        except chat_room.DoesNotExist:
            return Response(
                {"status": "404", "message": "Chat room not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    # 결과지 상세 조회
    @swagger_auto_schema(
        operation_id="사용자의 결과를 상세 조회하는 API",
        responses={
            200: openapi.Response(
                description="상세 조회 성공",
                examples={
                    "application/json": {
                        "status": "200",
                        "message": "결과 조회 성공",
                        "room_id": 1,
                        "name": "string",
                        "result": "string",
                        "image_url": "url"
                    }
                }
            )
        }
    )
    def get(self, request, room_id):
        try:
            chat_room_instance = chat_room.objects.get(id=room_id)
            result = chat_room_instance.result
            user_name = request.user.name

            response_data = {
                "status": "200",
                "message": "결과 조회 성공",
                "room_id": chat_room_instance.id,
                "name": user_name,
                "result": result,
                "image_url": photo.objects.get(chat_room_id=room_id).image_url
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except chat_room.DoesNotExist:
            return Response({"status": "404", "message": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)




