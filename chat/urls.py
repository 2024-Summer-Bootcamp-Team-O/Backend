from django.urls import path
from . import views

app_name = "apps"

urlpatterns = [
    path('start', views.CreateChatRoomView.as_view(), name='start-chat'),
    path('next', views.NextEpisodeView.as_view(), name='next-chat'),
    path('', views.IndexView.as_view(), name='index'),
]
