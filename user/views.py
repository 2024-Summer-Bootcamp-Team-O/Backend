from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import chat_room
from user.models import user
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserRegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer


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
        if not refresh_token:
            return Response(
                {"message": "리프레시 토큰이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {"message": "로그아웃되었습니다."}, status=status.HTTP_205_RESET_CONTENT
        )


# 해당 API는 JWT 예시를 보여주기 위한 코드입니다.
# 사용자 인증이 필요한 경우에 해당 코드를 참고하여 진행하시면 됩니다.
class ProfileView(APIView):

    @swagger_auto_schema(
        operation_id="프로필 조회를 위한 API",
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description="Bearer 토큰 (예: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...)",
                required=True,
            ),
        ],
    )
    def get(self, request):
        return Response(
            {
                "email": request.user.email,
                "name": request.user.name,
            },
            status=status.HTTP_200_OK,
        )

    def get_permissions(self):
        if self.request.method == "GET":
            self.authentication_classes = [JWTAuthentication]
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()



#결과페이지 조회
class UserResultView(APIView):
    @swagger_auto_schema(
        operation_id="사용자의 대화 결과를 조회하는 API"
    )
    def get(self, request):
        try:
            chat_room_instance = chat_room.objects.get(user_id=1) # user_id 하드코딩-> 수정필요함

            result = chat_room_instance.result
            room_id = chat_room_instance.id

            response_data = {
                "status": "200",
                "message": "결과 조회 성공",
                "data": [
                    {
                        "room_id": room_id,
                        "result": result
                    }
                ]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except chat_room.DoesNotExist:
            return Response({"status": "404", "message": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteUserResultView(APIView):
    @swagger_auto_schema(
        operation_id="결과를 삭제하는 API",
        responses={200: "삭제 성공"}
    )

    def delete(self, request, room_id):
        try:
            chat_room_instance = chat_room.objects.get(id=room_id)
            chat_room_instance.result = ""
            chat_room_instance.save()
            response_data = {
                "status": "200",
                "message": "삭제 성공"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except chat_room.DoesNotExist:
            return Response({"status": "404", "message": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)

