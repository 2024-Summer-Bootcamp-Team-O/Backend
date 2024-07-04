from rest_framework import generics, status
from rest_framework.response import Response
from user.models import member
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserRegistrationSerializer


class UserRegistrationView(APIView):

    @swagger_auto_schema(
        operation_id="회원가입을 위한 API",
        request_body=UserRegistrationSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckUserEmailView(APIView):
    @swagger_auto_schema(
        operation_description="이메일 중복 확인 API",
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
