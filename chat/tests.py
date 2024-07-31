from unittest import mock

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from chat.models import chat_room, episode
from user.models import user


class CreateChatRoomTest(TestCase):
    def setUp(self):
        # 테스트 클라이언트 생성
        self.client = APIClient()
        self.url = reverse('apps:start-chat')

        # User 모델의 manager를 mocking
        self.user_manager_patcher = mock.patch('user.models.user.objects')
        self.mock_user_manager = self.user_manager_patcher.start()
        self.mock_user_manager.create_user.return_value = user(id=1, email="testuser@example.com", name="testuser", password="testpass")

        # 사용자 정보 만들기
        self.user = self.mock_user_manager.create_user(email="testuser@example.com", name="testuser", password="testpass")
        # 테스트 클라이언트에 사용자 정보 넣기
        self.client.force_authenticate(user=self.user)

        # Redis를 mocking
        self.redis_patcher = mock.patch('chat.views.r', autospec=True)
        self.mock_redis = self.redis_patcher.start()
        # 외부 서버와 통신하는 requests를 mocking
        self.requests_patcher = mock.patch('chat.views.requests', autospec=True)
        self.mock_requests = self.requests_patcher.start()

        # JWT 토큰을 설정하여 인증 문제 해결
        self.client.credentials(HTTP_AUTHORIZATION='Bearer test_jwt_token')

        # 파일 읽기를 mocking
        self.open_patcher = mock.patch('builtins.open', mock.mock_open(read_data='1.0.0'))
        self.mock_open = self.open_patcher.start()

    def tearDown(self):
        # mocking된 Redis와 requests를 정리
        self.redis_patcher.stop()
        self.requests_patcher.stop()
        self.user_manager_patcher.stop()
        self.open_patcher.stop()

    @mock.patch('chat.views.get_gpt_message')
    @mock.patch('chat.views.chat_room.objects.create')
    def test_create_chat_room(self, mock_chat_room_create, mock_get_gpt_message):
        # 가짜 채팅방 객체를 생성
        mock_chat_room_instance = mock.Mock()
        mock_chat_room_instance.id = 1
        mock_chat_room_instance.character_id = 1
        mock_chat_room_create.return_value = mock_chat_room_instance

        # 가짜 GPT 응답 설정
        mock_response = mock.Mock()
        mock_response.status_code = status.HTTP_202_ACCEPTED
        mock_response.json.return_value = {"some_key": "some_value"}
        mock_get_gpt_message.return_value = mock_response

        # 요청 데이터
        payload = {"character_id": 1}
        # 채팅방 생성 요청 전송
        response = self.client.post(reverse('apps:start-chat'), payload, format='json')

        # 응답 상태가 201인지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 응답 데이터가 올바른지 확인
        self.assertEqual(response.json(), {"character_id": 1})
        mock_chat_room_create.assert_called_once_with(user_email=self.user.email, character_id=1)
        # Redis에 값이 올바르게 저장되었는지 확인
        self.mock_redis.set.assert_any_call(f"room_id:{self.user.email}", 1)
        self.mock_redis.set.assert_any_call(f"character_id:{self.user.email}", 1)


class NextEpisodeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('apps:next-chat')

        self.user_manager_patcher = mock.patch('user.models.user.objects')
        self.mock_user_manager = self.user_manager_patcher.start()
        self.mock_user_manager.create_user.return_value = user(id=1, email="testuser@example.com", name="testuser", password="testpass")

        self.user = self.mock_user_manager.create_user(email="testuser@example.com", name="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

        self.redis_patcher = mock.patch('chat.views.r', autospec=True)
        self.mock_redis = self.redis_patcher.start()
        self.requests_patcher = mock.patch('chat.views.requests', autospec=True)
        self.mock_requests = self.requests_patcher.start()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer test_jwt_token')

    def tearDown(self):
        self.redis_patcher.stop()
        self.requests_patcher.stop()
        self.user_manager_patcher.stop()

    @mock.patch('chat.views.chat_room.objects.get')
    @mock.patch('chat.views.episode.objects.get')
    @mock.patch('chat.views.chat_episode.objects.create')
    def test_next_episode(self, mock_chat_episode_create, mock_episode_get, mock_chat_room_get):
        # Redis에서 값을 가져오는 것을 가짜로 생성
        self.mock_redis.get.side_effect = lambda key: {
            f"character_id:{self.user.email}": b'1',
            f"room_id:{self.user.email}": b'1',
            f"count:{self.user.email}": b'0'
        }.get(key)
        # 가짜 채팅방 객체 생성
        mock_chat_room_instance = mock.Mock(spec=chat_room)
        mock_chat_room_instance.id = 1
        mock_chat_room_instance._state = mock.Mock()
        # 가짜 에피소드 객체 생성
        mock_episode_instance = mock.Mock(spec=episode)
        mock_episode_instance.id = 1
        mock_episode_instance._state = mock.Mock()
        # 가짜 채팅방 객체를 반환하도록 설정
        mock_chat_room_get.return_value = mock_chat_room_instance
        # 가짜 에피소드 객체를 반환하도록 설정
        mock_episode_get.return_value = mock_episode_instance

        # 다음 에피소드를 불러오는 요청 전송
        response = self.client.get(self.url)
        # 응답 상태가 201인지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 가짜 에피소드 생성이 호출되었는지 확인
        mock_chat_episode_create.assert_called_once_with(
            chat_room=mock_chat_room_instance,
            episode=mock_episode_instance
        )
        # Redis의 대화 기록이 삭제되었는지 확인
        self.mock_redis.delete.assert_called_once_with("conversation_history")


class GetFeedbackTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('apps:gpts-feedbacks')

        self.user_manager_patcher = mock.patch('user.models.user.objects')
        self.mock_user_manager = self.user_manager_patcher.start()
        self.mock_user_manager.create_user.return_value = user(id=1, email="testuser@example.com", name="testuser", password="testpass")

        self.user = self.mock_user_manager.create_user(email="testuser@example.com", name="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

        self.redis_patcher = mock.patch('chat.views.r', autospec=True)
        self.mock_redis = self.redis_patcher.start()
        self.requests_patcher = mock.patch('chat.views.requests', autospec=True)
        self.mock_requests = self.requests_patcher.start()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer test_jwt_token')

    def tearDown(self):
        self.redis_patcher.stop()
        self.requests_patcher.stop()
        self.user_manager_patcher.stop()

    @mock.patch('chat.views.get_gpt_feedback')
    def test_get_feedback(self, mock_get_gpt_feedback):
        # 가짜 GPT 피드백 응답 생성
        mock_get_gpt_feedback.return_value.status_code = status.HTTP_202_ACCEPTED

        # 피드백을 가져오는 요청 전송
        response = self.client.get(reverse('apps:gpts-feedbacks'))

        # 응답 상태가 201인지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 응답 데이터가 올바른지 확인
        self.assertEqual(response.data, "피드백이 생성되었습니다.")
        # 가짜 GPT 피드백 요청이 호출되었는지 확인
        mock_get_gpt_feedback.assert_called_once()


class ResultChatTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('apps:result-chat')

        self.user_manager_patcher = mock.patch('user.models.user.objects')
        self.mock_user_manager = self.user_manager_patcher.start()
        self.mock_user_manager.create_user.return_value = user(id=1, email="testuser@example.com", name="testuser", password="testpass")

        self.user = self.mock_user_manager.create_user(email="testuser@example.com", name="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

        self.redis_patcher = mock.patch('chat.views.r', autospec=True)
        self.mock_redis = self.redis_patcher.start()
        self.requests_patcher = mock.patch('chat.views.requests', autospec=True)
        self.mock_requests = self.requests_patcher.start()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer test_jwt_token')

    def tearDown(self):
        self.redis_patcher.stop()
        self.requests_patcher.stop()
        self.user_manager_patcher.stop()

    @mock.patch('chat.views.photo.objects.get')
    @mock.patch('chat.views.chat_room.objects.get')
    @mock.patch('chat.views.get_gpt_result')
    def test_result_chat(self, mock_get_gpt_result, mock_chat_room_get, mock_photo_get):
        # Redis에서 room_id를 가짜로 가져오기
        self.mock_redis.get.return_value = b'1'
        # 가짜 GPT 결과 응답 생성
        mock_get_gpt_result.return_value.json.return_value = {"result": "Some result"}
        mock_get_gpt_result.return_value.status_code = status.HTTP_200_OK

        # 가짜 채팅방 객체를 생성
        mock_chat_room_instance = mock.Mock()
        mock_chat_room_instance.id = 1
        # 가짜 사진 객체를 생성
        mock_photo_instance = mock.Mock()
        mock_photo_instance.image_url = "http://example.com/photo.jpg"
        mock_chat_room_get.return_value = mock_chat_room_instance
        mock_photo_get.return_value = mock_photo_instance

        # Redis 초기화, flsuhall을 호출하도록 설정
        self.mock_redis.flushall.return_value = True
        self.mock_redis.flushall()

        # 대화 결과를 가져오는 요청을 생성
        response = self.client.get(reverse('apps:result-chat'))

        # 응답 상태가 200인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 데이터가 올바른지 확인
        self.assertEqual(response.json(), {
            "result": "Some result",
            "image_url": "http://example.com/photo.jpg",
            "name": self.user.name,
            "room_id": 1
        })
        # 가짜 GPT 결과 요청이 호출되었는지 확인
        mock_get_gpt_result.assert_called_once()
        # 가짜 채팅방이 호출되었는지 확인
        mock_chat_room_get.assert_called_once()
        # 가짜 사진이 호출되었는지 확인
        mock_photo_get.assert_called_once()
        # Redis가 초기화되었는지 확인
        self.mock_redis.flushall.assert_called_once()


class UploadPhotoTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('apps:get-photos')

        self.user_manager_patcher = mock.patch('user.models.user.objects')
        self.mock_user_manager = self.user_manager_patcher.start()
        self.mock_user_manager.create_user.return_value = user(id=1, email="testuser@example.com", name="testuser", password="testpass")

        self.user = self.mock_user_manager.create_user(email="testuser@example.com", name="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

        self.redis_patcher = mock.patch('chat.views.r', autospec=True)
        self.mock_redis = self.redis_patcher.start()
        self.requests_patcher = mock.patch('chat.views.requests', autospec=True)
        self.mock_requests = self.requests_patcher.start()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer test_jwt_token')

    def tearDown(self):
        self.redis_patcher.stop()
        self.requests_patcher.stop()
        self.user_manager_patcher.stop()

    @mock.patch('chat.views.upload_to_s3')
    @mock.patch('chat.views.photo.objects.create')
    @mock.patch('chat.views.UploadPhotoSerializer')
    def test_upload_photo(self, mock_photo_create, mock_upload_to_s3, mock_upload_photo_serializer):
        # 가짜 S3 업로드 응답 생성
        mock_upload_to_s3.return_value = "http://example.com/photo.jpg"
        # 가짜 사진 객체를 생성
        mock_photo_instance = mock.Mock()
        mock_photo_create.return_value = mock_photo_instance

        # 인메모리 파일 생성
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile

        file = BytesIO(b"dummy image data")
        file.seek(0)
        image = SimpleUploadedFile("image.jpg", file.read(), content_type="image/jpeg")

        # 시리얼라이저 mocking 설정
        mock_serializer_instance = mock.Mock()
        mock_upload_photo_serializer.return_value = mock_serializer_instance
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {'image': image}
        mock_serializer_instance.save.return_value = mock_photo_instance

        # __getitem__ 설정
        def mock_getitem(key):
            return mock_serializer_instance.validated_data[key]
        mock_serializer_instance.__getitem__.side_effect = mock_getitem

        # 사진 업로드 요청 전송
        response = self.client.post(reverse('apps:get-photos'), {'image': image}, format='multipart')

        # 응답 상태가 200인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 데이터가 올바른지 확인
        self.assertEqual(response.json(), {
            "message": "사진이 업로드 되었습니다.",
            "url": "http://example.com/photo.jpg"
        })

        # 시리얼라이저가 올바르게 호출되었는지 확인
        mock_upload_photo_serializer.assert_called_once_with(data={'image': image})
        mock_serializer_instance.is_valid.assert_called_once()
        mock_serializer_instance.save.assert_called_once()

        # 가짜 S3 업로드가 호출되었는지 확인
        mock_upload_to_s3.assert_called_once()
        # 가짜 사진 생성이 호출되었는지 확인
        mock_photo_create.assert_called_once()
        # 추가 : Redis에 값이 올바르게 저장되었는지 확인
        self.mock_redis.set.assert_called_with(f"photo_url:{self.user.email}", "http://example.com/photo.jpg")