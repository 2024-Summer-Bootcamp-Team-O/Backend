from django.urls import path

from gpt import views

app_name = "gpt"

urlpatterns = [
    path("talk", views.GetGPTTalkView.as_view(), name="gpt-talk"),
    path("answer", views.GetGPTAnswerView.as_view(), name="gpt-answer"),
    path("result", views.GetGPTResultView.as_view(), name="gpt-result"),
]
