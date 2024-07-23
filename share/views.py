from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import chat_room, photo


# Create your views here.

class ShareResultView(APIView):

    @swagger_auto_schema(
        operation_id="공유된 결과지를 조회하는 API",
        responses={
            200: openapi.Response(
                description="조회 성공",
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
            user_name = chat_room_instance.user.name

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
