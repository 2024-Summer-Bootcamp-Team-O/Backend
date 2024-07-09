import requests
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .serializers import AnswerSerializer


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
