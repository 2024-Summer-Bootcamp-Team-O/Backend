from django.urls import path
from . import views

appname = "chat"

urlpatterns = [
    path('answers', views.AnswerView.as_view(), name='choice'),
    path('start', views.CreateChatRoomView.as_view(), name='start_chat'),
    path('next', views.NextEpisodeView.as_view(), name='next_chat')
]
