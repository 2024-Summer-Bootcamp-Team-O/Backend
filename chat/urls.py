from django.urls import path

from . import views

appname = "chat"

urlpatterns = [
    path('gpt-talk', views.GetGPTTalkView.as_view(), name='gpt-talk'),
    path('gpt-answer', views.GetGPTAnswerView.as_view(), name='gpt-answer'),
]
