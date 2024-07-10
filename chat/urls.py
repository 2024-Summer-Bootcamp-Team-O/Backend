from django.urls import path
from .views import CreateChatRoomView
from . import views

appname = "chat"

urlpatterns = [
    path('answers', views.AnswerView.as_view(), name='choice'),
    path('start', CreateChatRoomView.as_view(), name='start_chat')
]
