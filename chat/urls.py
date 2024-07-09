from django.urls import path

from . import views

appname = "chat"

urlpatterns = [
    path('gpt-talk', views.GetGPTTalkView.as_view(), name='gpt-talk'),
    path('gpt-answer', views.GetGPTAnswerView.as_view(), name='gpt-answer'),
    # gpt-choice는 실제로 Url로 호출되지 않고, WebSocket을 통해 호출됩니다.
    # client가 구현된 이후에 제거할 예정입니다.
    path('gpt-choice', views.GetGPTChoiceView.as_view(), name='gpt-choice'),
]
