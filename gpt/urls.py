from django.urls import path

from gpt import views

app_name = "gpt"

urlpatterns = [
    path("messages", views.GetGPTMessageView.as_view(), name="gpt-message"),
    path("feedbacks", views.GetGPTFeedbackView.as_view(), name="gpt-feedback"),
    path("results", views.GetGPTResultView.as_view(), name="gpt-result"),
]
