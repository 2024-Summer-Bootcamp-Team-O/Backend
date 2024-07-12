import requests
import redis
from django.http import JsonResponse
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from django.db.models.functions import Random
from .models import episode
from .serializers import ChatRoomSerializer


r = redis.Redis(host='redis', port=6379, db=0)


# 웹소켓 테스트용 api
class IndexView(APIView):
    def get(self, request):
        return render(request, 'index.html')


class CreateChatRoomView(APIView):
    @swagger_auto_schema(
        request_body=ChatRoomSerializer,
        operation_id='대화시작 시 캐릭터 정보를 저장하고 상황을 랜덤 배정하는 API',
    )
    def post(self, request, *args, **kwargs):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            # 데이터베이스에 직렬화하여 저장
            chat_room_instance = serializer.save()
            r.set('room_id', chat_room_instance.room_id)
            # 저장된 데이터에서 character_id 추출
            character_id = chat_room_instance.character_id
            r.set('character_id', character_id)
            r.set('count', 0)
            response = get_next_episode(request)
            if response.status_code == status.HTTP_202_ACCEPTED:
                return JsonResponse({
                    'character_id': character_id,
                }, status=status.HTTP_201_CREATED)
            return JsonResponse(response.json(), status=response.status_code)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NextEpisodeView(APIView):
    @swagger_auto_schema(
        operation_id='다음 상황을 랜덤 제공하는 API',
    )
    def get(self, request):
        character_id = r.get('character_id').decode('utf-8')

        count = int(r.get('count'))
        next_episode_time_id = get_next_episode_time_id(count)
        next_episode_id = get_random_episode_id(next_episode_time_id)

        response = get_gpt_message(request, character_id, next_episode_id)
        if response.status_code == status.HTTP_202_ACCEPTED:
            return JsonResponse({
                'character_id': character_id,
            }, status=status.HTTP_201_CREATED)
        return JsonResponse(response.json(), status=response.status_code)


def get_next_episode_time_id(count):
    return count + 1


def get_gpt_message(request, character_id, episode_id):
    url = request.build_absolute_uri(reverse('gpt:gpt-message'))
    payload = {
        "character_id": character_id,
        "episode_id": episode_id
    }
    headers = {
        'Content-Type': 'application/json',
    }
    return requests.post(url, json=payload, headers=headers)


def get_gpt_answer(request, choice_content):
    url = request.build_absolute_uri(reverse('gpt:gpt-answer'))
    payload = {
        "choice_content": choice_content
    }
    headers = {
        'Content-Type': 'application/json',
    }
    return requests.post(url, json=payload, headers=headers)


def get_next_episode(request):
    url = request.build_absolute_uri(reverse('apps:next-chat'))
    headers = {
        'Content-Type': 'application/json',
    }
    return requests.get(url, headers=headers)


def get_random_episode_id(episode_time_id):
    random_episode = episode.objects.filter(episode_time_id=episode_time_id).order_by(Random()).first()
    if random_episode is None:
        return None
    return random_episode.episode_id
