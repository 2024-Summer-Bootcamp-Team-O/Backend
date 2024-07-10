import requests
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from django.db.models.functions import Random
from .models import character,episode

from .serializers import AnswerSerializer
from  .serializers import ChatRoomSerializer

# episode 랜덤 함수
def get_random_episode_id(episode_time_id):
    random_episode = episode.objects.filter(episode_time_id=episode_time_id).order_by(Random()).first()
    if random_episode is None:
        return None
    return random_episode.episode_id


class CreateChatRoomView(APIView):
    @swagger_auto_schema(
        request_body=ChatRoomSerializer,
        operation_id='대화시작 시 캐릭터 정보를 저장하고 상황을 랜덤 배정하는 API',
    )
    def post(self, request,*args, **kwargs):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            # 데이터베이스에 직렬화하여 저장
            chat_room_instance = serializer.save()

            # 저장된 데이터에서 character_id 추출
            character_id = chat_room_instance.character.character_id

            # 추출한 character_id를 가진 character 객체의 work_id 값 추출
            character_instance = character.objects.get(character_id=character_id)
            work_id = character_instance.work.work_id

            if work_id == 1:  # 회사일 때
                # episode_time_id = 1(출근)인 episode 객체의 episode_id 값 랜덤으로 가져오기
                episode_id = get_random_episode_id(1)
            else:  # 알바일 때
                # episode_time_id = 5(고기집)인 episode 객체의 episode_id 값 랜덤으로 가져오기
                episode_id = get_random_episode_id(5)

            if episode_id is not None:
                # GPT Message API 호출
                url = request.build_absolute_uri(reverse('gpt:gpt-message'))
                payload = {
                    "character_id": character_id,
                    "episode_id": episode_id
                }
                headers = {
                    'Content-Type': 'application/json',
                }
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == status.HTTP_202_ACCEPTED:
                    return JsonResponse({
                        'character_id': character_instance.character_id,
                    }, status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse(response.json(), status=response.status_code)
            else:
                return JsonResponse({'error': 'No episode found for the given episode_time_id'},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnswerView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='답변과 피드백을 가져오는 API',
        request_body=AnswerSerializer,
    )
    def post(self, request):
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            choice_content = serializer.validated_data.get('choice_content')
            mz_percent = serializer.validated_data.get('mz_percent')
            url = request.build_absolute_uri(reverse('gpt:gpt-answer'))
            payload = {
                "choice_content": choice_content,
                "mz_percent": mz_percent
            }
            headers = {
                'Content-Type': 'application/json',
                # 'Authorization': 'Bearer ' + request.headers['Authorization']
            }
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == status.HTTP_202_ACCEPTED:
                return JsonResponse({'task_id': response.json().get('task_id')}, status=status.HTTP_200_OK)
            else:
                return JsonResponse(response.json(), status=response.status_code)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
