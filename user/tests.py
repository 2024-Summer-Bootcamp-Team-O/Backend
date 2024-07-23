from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from user.models import user
from user.views import LogoutView


# 회원가입 테스트
class UserRegistrationViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('sign-up')

    @patch('user.serializers.make_password')
    @patch('user.models.user.objects.create')
    def test_registration(self, mock_create_user, mock_make_password):
        # 사용자 인스턴스 생성 및 비밀번호 해시 함수를 목킹
        mock_user_instance = MagicMock()
        mock_create_user.return_value = mock_user_instance

        # make_password 함수가 고정된 해시 값을 반환하도록 설정
        mock_make_password.return_value = 'hashed_password'

        data = {
            "email": "test@example.com",
            "password": "testpassword",
            "name": "Test User"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "회원가입에 성공하였습니다.")

        # 고정된 해시 값을 사용하여 비교
        mock_create_user.assert_called_once_with(
            email="test@example.com",
            password='hashed_password',
            name="Test User"
        )

# 이메일 중복 확인 테스트
class CheckUserEmailViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('exist')

    @patch('user.models.user.objects.filter')  # user 모델의 filter 메서드를 목킹
    def test_check_email_available(self, mock_filter):
        # filter 메서드가 호출될 때 exists 메서드가 False를 반환하도록 설정 (이메일이 존재하지 않는 경우)
        mock_filter.return_value.exists.return_value = False

        # 이메일 중복 확인 요청 보내기
        response = self.client.get(self.url, {'email': 'new@example.com'})

        # 응답 메시지 및 200 (OK)인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "사용 가능한 이메일입니다")

    @patch('user.models.user.objects.filter')
    def test_check_email_exists(self, mock_filter):
        # filter 메서드가 호출될 때 exists 메서드가 True를 반환하도록 설정 (이메일이 존재하는 경우)
        mock_filter.return_value.exists.return_value = True

        # 이메일 중복 확인 요청 보내기
        response = self.client.get(self.url, {'email': 'test@example.com'})

        # 응답 메시지 및 409 (Conflict)인지 확인
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["message"], "이미 존재하는 이메일입니다")


# 로그인 테스트
class LoginViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('login')

    @patch('user.models.user.objects.get')
    @patch('user.serializers.check_password')
    @patch('rest_framework_simplejwt.tokens.RefreshToken.for_user')
    def test_login(self, mock_for_user, mock_check_password, mock_get_user):
        # 사용자 인스턴스와 관련 메서드들을 목킹
        mock_user_instance = MagicMock()
        mock_get_user.return_value = mock_user_instance
        mock_check_password.return_value = True

        # RefreshToken의 access 및 refresh 토큰을 목킹
        mock_refresh_token = MagicMock()
        mock_refresh_token.access_token = 'access_token'
        mock_refresh_token.__str__.return_value = 'refresh_token'
        mock_for_user.return_value = mock_refresh_token

        data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        mock_get_user.assert_called_once_with(email="test@example.com")
        mock_check_password.assert_called_once_with("testpassword", mock_user_instance.password)


# 로그아웃 테스트
class LogoutViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('logout')

    @patch('user.views.RefreshToken')
    def test_logout(self, mock_refresh_token):
        # RefreshToken 클래스와 관련 메서드들을 목킹
        mock_token_instance = MagicMock()
        mock_refresh_token.return_value = mock_token_instance

        data = {
            "refresh": "dummy_refresh_token"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data, {"message": "로그아웃되었습니다."})
        mock_refresh_token.assert_called_once_with("dummy_refresh_token")
        mock_token_instance.blacklist.assert_called_once()

    def test_logout_no_refresh_token(self):
        # 리프레시 토큰이 없는 경우에 대한 테스트
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "리프레시 토큰이 필요합니다."})


# 결과 페이지 조회 테스트
class UserResultViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('result')  # 결과 조회 URL 설정
        self.user = MagicMock()  # 목킹된 사용자 객체 생성
        self.client.force_authenticate(user=self.user)  # 목킹된 사용자로 인증 강제

    @patch('chat.models.chat_room.objects.filter')  # chat_room 모델의 filter 메서드를 목킹
    def test_get_user_result(self, mock_filter):
        # 목킹된 chat_room 객체 생성
        mock_chat_room_instance = MagicMock()
        mock_chat_room_instance.id = 1
        mock_chat_room_instance.character_id = 1
        mock_chat_room_instance.user.name = "Test User"
        # filter 메서드가 호출될 때 chat_room 객체 리스트 반환
        mock_filter.return_value = [mock_chat_room_instance]

        @patch('chat.models.photo.objects.get')  # photo 모델의 get 메서드를 목킹
        def test_get_photo(self, mock_get_photo):
            # 목킹된 photo 객체 생성
            mock_photo_instance = MagicMock()
            mock_photo_instance.image_url = "http://example.com/image.jpg"
            # get 메서드가 호출될 때 목킹된 photo 객체 반환
            mock_get_photo.return_value = mock_photo_instance

            # 결과 조회 요청 보내기
            response = self.client.get(self.url)

            # 응답이 200 (OK)인지 확인
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # 응답 데이터에 올바른 결과가 포함되어 있는지 확인
            self.assertEqual(response.data["data"][0]["room_id"], 1)
            self.assertEqual(response.data["data"][0]["character_id"], 1)
            self.assertEqual(response.data["data"][0]["name"], "Test User")
            self.assertEqual(response.data["data"][0]["image_url"], "http://example.com/image.jpg")


# 상세 조회 테스트
class UserDetailResultViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('result-detail', kwargs={'room_id': 1})  # 결과 상세 조회 URL 설정
        self.user = MagicMock()  # 목킹된 사용자 객체 생성
        self.client.force_authenticate(user=self.user)  # 목킹된 사용자로 인증 강제

    @patch('chat.models.chat_room.objects.get')  # chat_room 모델의 get 메서드를 목킹
    def test_get_user_detail_result(self, mock_get):
        # 목킹된 chat_room 객체 생성
        mock_chat_room_instance = MagicMock()
        mock_chat_room_instance.id = 1
        mock_chat_room_instance.result = "Test Result"
        mock_chat_room_instance.user.name = "Test User"
        # get 메서드가 호출될 때 목킹된 chat_room 객체 반환
        mock_get.return_value = mock_chat_room_instance

        @patch('chat.models.photo.objects.get')  # photo 모델의 get 메서드를 목킹
        def test_get_photo(self, mock_get_photo):
            # 목킹된 photo 객체 생성
            mock_photo_instance = MagicMock()
            mock_photo_instance.image_url = "http://example.com/image.jpg"
            # get 메서드가 호출될 때 목킹된 photo 객체 반환
            mock_get_photo.return_value = mock_photo_instance

            # 결과 상세 조회 요청 보내기
            response = self.client.get(self.url)

            # 응답이 200 (OK)인지 확인
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # 응답 데이터에 올바른 결과가 포함되어 있는지 확인
            self.assertEqual(response.data["room_id"], 1)
            self.assertEqual(response.data["name"], "Test User")
            self.assertEqual(response.data["result"], "Test Result")
            self.assertEqual(response.data["image_url"], "http://example.com/image.jpg")

    @patch('chat.models.chat_room.objects.get')  # chat_room 모델의 get 메서드를 목킹
    def test_delete_user_result(self, mock_get):
        # 목킹된 chat_room 객체 생성
        mock_chat_room_instance = MagicMock()
        mock_chat_room_instance.id = 1
        # get 메서드가 호출될 때 목킹된 chat_room 객체 반환
        mock_get.return_value = mock_chat_room_instance

        # 결과 삭제 요청 보내기
        response = self.client.delete(self.url)

        # 응답이 200 (OK)인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 메시지가 올바른지 확인
        self.assertEqual(response.data["message"], "삭제 성공")
