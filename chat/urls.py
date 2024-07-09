from django.urls import path

from . import views

appname = "chat"

urlpatterns = [
    path('answer', views.AnswerView.as_view(), name='choice'),
]
