from django.urls import path

from . import views

appname = "chat"

urlpatterns = [
    path('answers', views.AnswerView.as_view(), name='choice'),
]
