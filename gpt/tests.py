# gpt/tests.py
import redis
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import unittest
from unittest.mock import patch, Mock
from django.test import TransactionTestCase, override_settings
from unittest.mock import patch, MagicMock, AsyncMock
from gpt.consumers import ChatConsumer
from channels.testing import WebsocketCommunicator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from rest_framework_simplejwt.tokens import AccessToken
from gpt.tasks import get_gpt_message, get_gpt_answer, get_gpt_feedback, get_gpt_result, load_memory, text_to_speech_file
from chat.models import voice
from base64 import b64encode


# GPT 대사를 가져오는 테스트
class GetGPTMessageViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('gpt:gpt-message')

        # 인증 헤더 설정
        self.client.credentials(HTTP_AUTHORIZATION='Bearer testtoken')

        # 유효한 요청 데이터 설정
        self.valid_payload = {
            'character_id': 1,
            'episode_id': 1
        }
        # 유효하지 않은 요청 데이터 설정
        self.invalid_payload = {
            'character_id': '',
            'episode_id': ''
        }

    @patch('gpt.views.get_gpt_message.delay')
    @patch('gpt.views.redis.Redis')
    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate')
    def test_create_valid_gpt_message(self, mock_authenticate, mock_redis, mock_get_gpt_message):
        """
        유효한 요청 데이터를 사용하여 GPT 메시지 생성 요청을 보낸 후,
        202 ACCEPTED 상태 코드와 task_id를 포함한 응답을 확인합니다.
        """
        # 사용자 인증을 모킹
        mock_user = MagicMock()
        mock_user.email = 'testuser@example.com'
        mock_authenticate.return_value = (mock_user, None) # 사용자가 인증되었음을 모킹

        # Celery 태스크의 모킹된 반환값을 설정
        mock_get_gpt_message.return_value.task_id = '12345'

        # Redis 클라이언트를 모킹
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        # 유효한 요청 데이터를 POST 요청으로 전송
        response = self.client.post(self.url, data=self.valid_payload, format='json')

        # Redis 동작 검증
        user_email = mock_user.email
        episode_id_key = f"episode_id:{user_email}"
        count_key = f"count:{user_email}"
        character_id_key = f"character_id:{user_email}"

        # Redis 호출 확인
        mock_redis_instance.exists.assert_any_call(episode_id_key)
        mock_redis_instance.delete.assert_any_call(episode_id_key)
        mock_redis_instance.set.assert_any_call(episode_id_key, 1)
        mock_redis_instance.exists.assert_any_call(count_key)
        mock_redis_instance.incr.assert_called_with(count_key)
        mock_redis_instance.set.assert_any_call(character_id_key, 1)

        # 응답 상태 코드가 202 ACCEPTED인지 확인
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # 응답 데이터에 task_id가 포함되어 있는지 확인
        self.assertIn('task_id', response.json())

    @patch('gpt.views.redis.Redis')
    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate')
    def test_create_invalid_gpt_message(self, mock_authenticate, mock_redis):
        """
        유효하지 않은 요청 데이터를 사용하여 GPT 메시지 생성 요청을 보낸 후,
        400 BAD REQUEST 상태 코드를 확인합니다.
        """
        # 사용자 인증을 모킹
        mock_user = MagicMock()
        mock_user.email = 'testuser@example.com'
        mock_authenticate.return_value = (mock_user, None)

        # 유효하지 않은 요청 데이터를 POST 요청으로 전송
        response = self.client.post(self.url, data=self.invalid_payload, format='json')

        # 응답 상태 코드가 400 BAD REQUEST인지 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# GPT의 피드백을 가져오는 테스트
class GetGPTFeedbackViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('gpt:gpt-feedback')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer testtoken')

    @patch('gpt.views.get_gpt_feedback.delay')
    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate')
    def test_get_feedback(self, mock_authenticate, mock_get_gpt_feedback):
        """
        피드백 요청을 보낸 후, 202 ACCEPTED 상태 코드와 task_id를 포함한 응답을 확인합니다.
        """
        # 사용자 인증을 모킹
        mock_user = MagicMock()
        mock_user.email = 'testuser@example.com'
        mock_authenticate.return_value = (mock_user, None)

        # Celery 태스크의 모킹된 반환값을 설정합니다.
        mock_get_gpt_feedback.return_value.task_id = '12345'

        # GET 요청을 전송합니다.
        response = self.client.get(self.url)

        # 응답 상태 코드가 202 ACCEPTED인지 확인합니다.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # 응답 데이터에 task_id가 포함되어 있는지 확인합니다.
        self.assertIn('task_id', response.json())

        # Celery 태스크가 올바르게 호출되었는지 확인합니다.
        mock_get_gpt_feedback.assert_called_once_with(mock_user.id)


# GPT의 최종 피드백을 가져오는 테스트
class GetGPTResultViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer testtoken')
        self.url = reverse('gpt:gpt-result')

    @patch('gpt.views.get_gpt_result')
    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.authenticate')
    def test_get_result(self, mock_authenticate, mock_get_gpt_result):
        """
        결과 요청을 보낸 후, 200 OK 상태 코드와 모킹된 결과를 포함한 응답을 확인합니다.
        """
        # 사용자 인증을 모킹
        mock_authenticate.return_value = (MagicMock(), None)
        # get_gpt_result 함수의 모킹된 반환값을 설정
        mock_get_gpt_result.return_value = 'Mocked GPT Result'

        # GET 요청을 전송
        response = self.client.get(self.url)

        # 응답 상태 코드가 200 OK인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 데이터가 모킹된 결과와 일치하는지 확인
        self.assertEqual(response.json(), {'result': 'Mocked GPT Result'})


# 라우팅 설정
application = ProtocolTypeRouter({
    "websocket": URLRouter([
        re_path(r'ws/gpt/$', ChatConsumer.as_asgi()),
    ]),
})

# consumer_test
@override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
class ChatConsumerUnitTest(TransactionTestCase):
    async def test_connect(self):
        """
        WebSocket 연결이 성공적으로 이루어지는지 테스트합니다.
        """
        # WebSocket 커뮤니케이터 생성
        communicator = WebsocketCommunicator(application, "/ws/gpt/")

        # WebSocket 연결 시도
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # 연결 종료
        await communicator.disconnect()

    @patch('gpt.tasks.get_gpt_answer.delay', new_callable=Mock)
    async def test_receive(self, mock_get_gpt_answer):
        """
        WebSocket을 통해 메시지를 전송하고, Celery 태스크가 올바르게 호출되는지 테스트합니다.
        """
        # WebSocket 커뮤니케이터 생성
        communicator = WebsocketCommunicator(application, "/ws/gpt/")

        # WebSocket 연결 시도
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # 메시지 보내기
        test_message = {'message': 'Test message', 'access': 'test_access_token'}
        await communicator.send_json_to(test_message)

        # 수신을 확인하기 위해 잠시 대기
        await communicator.receive_nothing()

        # Celery 태스크가 올바르게 호출되었는지 확인
        mock_get_gpt_answer.assert_called_once_with('Test message', 'test_access_token')

        # 연결 종료
        await communicator.disconnect()

    async def test_disconnect(self):
        """
        WebSocket 연결이 성공적으로 해제되는지 테스트합니다.
        """
        # WebSocket 커뮤니케이터 생성
        communicator = WebsocketCommunicator(application, "/ws/gpt/")

        # WebSocket 연결 시도
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # 연결 종료
        await communicator.disconnect()

    async def test_gpt_talk_message(self):
        """
        gpt_talk_message 이벤트가 올바르게 처리되는지 테스트합니다.
        """
        # WebSocket 커뮤니케이터 생성
        communicator = WebsocketCommunicator(application, "/ws/gpt/")

        # WebSocket 연결 시도
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # gpt_talk_message 이벤트 테스트
        event = {"type": "gpt_talk_message", "message": "Hello, GPT!"}
        await communicator.send_input(event)
        response = await communicator.receive_json_from()
        self.assertEqual(response, {"message": "Hello, GPT!", "type": "gpt_talk_message"})

        # 연결 종료
        await communicator.disconnect()

    async def test_gpt_answer_message(self):
        """
        gpt_answer_message 이벤트가 올바르게 처리되는지 테스트합니다.
        """
        # WebSocket 커뮤니케이터 생성
        communicator = WebsocketCommunicator(application, "/ws/gpt/")

        # WebSocket 연결 시도
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # gpt_answer_message 이벤트 테스트
        event = {"type": "gpt_answer_message", "message": "Here is the answer"}
        await communicator.send_input(event)
        response = await communicator.receive_json_from()
        self.assertEqual(response, {"message": "Here is the answer", "type": "gpt_answer_message"})

        # 연결 종료
        await communicator.disconnect()

    async def test_gpt_feedback_message(self):
        """
        gpt_feedback_message 이벤트가 올바르게 처리되는지 테스트합니다.
        """
        # WebSocket 커뮤니케이터 생성
        communicator = WebsocketCommunicator(application, "/ws/gpt/")

        # WebSocket 연결 시도
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # gpt_feedback_message 이벤트 테스트
        event = {"type": "gpt_feedback_message", "message": "This is feedback"}
        await communicator.send_input(event)
        response = await communicator.receive_json_from()
        self.assertEqual(response, {"message": "This is feedback", "type": "gpt_feedback_message"})

        # 연결 종료
        await communicator.disconnect()

    async def test_gpt_audio(self):
        """
        gpt_audio 이벤트가 올바르게 처리되는지 테스트합니다.
        """
        # WebSocket 커뮤니케이터 생성
        communicator = WebsocketCommunicator(application, "/ws/gpt/")

        # WebSocket 연결 시도
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # gpt_audio 이벤트 테스트
        event = {"type": "gpt_audio", "audio_chunk": "audio_data"}
        await communicator.send_input(event)
        response = await communicator.receive_json_from()
        self.assertEqual(response, {"audio_chunk": "audio_data", "type": "audio"})

        # 연결 종료
        await communicator.disconnect()


# task_test
@override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
class TasksUnitTest(TestCase):

    def setUp(self):
        # Mock Redis
        self.mock_redis = MagicMock()
        self.mock_redis.get = MagicMock()
        self.mock_redis.set = MagicMock()
        self.mock_redis.exists = MagicMock()
        self.mock_redis.keys = MagicMock()
        self.mock_redis.delete = MagicMock()

        # Mock OpenAI
        self.mock_openai = MagicMock()
        self.mock_openai.ChatCompletion.create = MagicMock()

        # Mock ElevenLabs
        self.mock_elevenlabs = MagicMock()
        self.mock_elevenlabs.text_to_speech.convert = MagicMock()

        # Mock memory
        self.mock_memory = MagicMock()
        self.mock_memory.chat_memory.messages = []
        self.mock_memory.buffer_as_messages = "test buffer messages"

        # Mock models
        self.mock_episode = MagicMock()
        self.mock_episode.objects.get.return_value.content = "test content"

        self.mock_character = MagicMock()
        self.mock_character.objects.get.return_value.script = "test script"

        self.mock_voice = MagicMock()
        self.mock_voice.objects.get.return_value = MagicMock(code="test_code", stability=0.5, similarity=0.5, style=0.5)

        # Patch objects
        patcher_redis = patch('gpt.tasks.r', self.mock_redis)
        patcher_openai = patch('gpt.tasks.openai', self.mock_openai)
        patcher_elevenlabs = patch('gpt.tasks.client', self.mock_elevenlabs)
        patcher_memory = patch('gpt.tasks.memory', self.mock_memory)
        patcher_episode = patch('gpt.tasks.episode', self.mock_episode)
        patcher_character = patch('gpt.tasks.character', self.mock_character)
        patcher_voice = patch('gpt.tasks.voice', self.mock_voice)
        patcher_text_to_speech_file = patch('gpt.tasks.text_to_speech_file', return_value=None)
        patcher_get_object_or_404 = patch('django.shortcuts.get_object_or_404', return_value=self.mock_voice.objects.get.return_value)
        patcher_channel_layer = patch('channels.layers.get_channel_layer', new_callable=lambda: self.mock_channel_layer())

        # Start patches
        self.addCleanup(patcher_redis.stop)
        self.addCleanup(patcher_openai.stop)
        self.addCleanup(patcher_elevenlabs.stop)
        self.addCleanup(patcher_memory.stop)
        self.addCleanup(patcher_episode.stop)
        self.addCleanup(patcher_character.stop)
        self.addCleanup(patcher_voice.stop)
        self.addCleanup(patcher_text_to_speech_file.stop)
        self.addCleanup(patcher_get_object_or_404.stop)
        self.addCleanup(patcher_channel_layer.stop)

        self.mock_redis = patcher_redis.start()
        self.mock_openai = patcher_openai.start()
        self.mock_elevenlabs = patcher_elevenlabs.start()
        self.mock_memory = patcher_memory.start()
        self.mock_episode = patcher_episode.start()
        self.mock_character = patcher_character.start()
        self.mock_voice = patcher_voice.start()
        self.mock_text_to_speech_file = patcher_text_to_speech_file.start()
        self.mock_get_object_or_404 = patcher_get_object_or_404.start()
        self.mock_channel_layer = patcher_channel_layer.start()

    def mock_channel_layer(self):
        channel_layer = MagicMock()
        channel_layer.group_send = AsyncMock()
        return channel_layer

    def test_get_gpt_message(self):
        character_id = 1
        episode_id = 1
        user_email = 'test@example.com'

        result = get_gpt_message(character_id, episode_id, user_email)

        self.assertIsNotNone(result)
        self.mock_openai.ChatCompletion.create.assert_called()

    def test_get_gpt_answer(self):
        user_message = 'Test message'
        access_token = 'test_token'
        mock_token = MagicMock()
        mock_token["user_email"] = 'test@example.com'

        # Mock Redis responses
        self.mock_redis.get.side_effect = lambda key: {
            f"character_id:{mock_token['user_email']}": b'1',
            f"episode_id:{mock_token['user_email']}": b'1',
            f"conversation_history:{mock_token['user_email']}": b"user: Hello\nassistant: Hi there!"
        }.get(key, None)
        self.mock_redis.keys.return_value = []

        with patch.object(AccessToken, '__init__', lambda self, token: None):
            with patch.object(AccessToken, 'verify', return_value=None):
                with patch.object(AccessToken, '__getitem__', lambda self, item: mock_token[item]):
                    result = get_gpt_answer(user_message, access_token)

        self.assertIsNotNone(result)
        self.mock_openai.ChatCompletion.create.assert_called()

    def test_get_gpt_feedback(self):
        user_email = 'test@example.com'
        self.mock_redis.get.return_value = b'1'
        self.mock_redis.keys.return_value = [b'feedback:test@example.com-1']

        result = get_gpt_feedback(user_email)

        self.assertIsNotNone(result)
        self.mock_openai.ChatCompletion.create.assert_called()

    def test_get_gpt_result(self):
        user_email = 'test@example.com'
        self.mock_redis.keys.return_value = [b'feedback:test@example.com-1', b'feedback:test@example.com-2']
        self.mock_redis.get.side_effect = [b'feedback 1', b'feedback 2']

        result = get_gpt_result(user_email)

        self.assertIsNotNone(result)
        self.mock_openai.ChatCompletion.create.assert_called()


def test_load_memory(self):
    user_email = 'test@example.com'
    self.mock_redis.get.return_value = b'user: Hello\nassistant: Hi there!\ninvalid message'

    load_memory(user_email)

    self.assertEqual(len(self.mock_memory.chat_memory.messages), 2)
    self.assertEqual(self.mock_memory.chat_memory.messages[0], {'role': 'user', 'content': 'Hello'})
    self.assertEqual(self.mock_memory.chat_memory.messages[1], {'role': 'assistant', 'content': 'Hi there!'})


def test_text_to_speech_file(self):
    text = "Hello, this is a test."
    character_id = 1

    with patch('gpt.tasks.get_object_or_404',
               return_value=self.mock_voice.objects.get.return_value) as mock_get_object_or_404:
        text_to_speech_file(text, character_id)
        mock_get_object_or_404.assert_called_once_with(voice, character_id=character_id)

    self.mock_elevenlabs.text_to_speech.convert.assert_called_once()


