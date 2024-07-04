from user.models import member
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserRegistrationSerializer
from django.contrib.auth import authenticate, login, logout
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
            return Response({"message": "회원가입에 성공하였습니다."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckUserEmailView(APIView):
    @swagger_auto_schema(
        operation_id="이메일 중복 확인 API",
        manual_parameters=[
            openapi.Parameter(
                "member_email",
                openapi.IN_QUERY,
                description="중복 확인할 이메일",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={200: "사용 가능한 이메일입니다", 409: "이미 존재하는 이메일입니다"},
    )
    def get(self, request, *args, **kwargs):
        member_email = request.query_params.get("member_email")
        if member.objects.filter(member_email=member_email).exists():
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
            user = serializer.validated_data["member"]
            request.session['member_id'] = user.member_id  # 세션에 사용자 ID 저장
            request.session.save()

            print(f"Session Data: {request.session.items()}")
            return Response({'message': '로그인에 성공하였습니다.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    @swagger_auto_schema(
        operation_id="로그아웃을 위한 API",
    )
    def post(self, request):
        logout(request)
        return Response({'message': '로그아웃에 성공하였습니다.'}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    def get(self, request):
        member_id = request.session.get("member_id")
        if member_id:
            return Response({'message': f'로그인된 유저: {member_id}'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': '로그인이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)

