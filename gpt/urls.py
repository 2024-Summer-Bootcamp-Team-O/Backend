from django.urls import path

from gpt import views

app_name = "gpt"

urlpatterns = [
    path("messages", views.GetGPTMessageView.as_view(), name="gpt-message"),
    path("answers", views.GetGPTAnswerView.as_view(), name="gpt-answer"),
    path("results", views.GetGPTResultView.as_view(), name="gpt-result"),
]
