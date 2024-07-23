from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import chat_room, photo


# Create your views here.

class ShareResultView(APIView):
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
