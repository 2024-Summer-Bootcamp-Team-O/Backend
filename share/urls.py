from share import views
from django.urls import path


appname = "share"


urlpatterns = [
    path("results/<int:room_id>", views.ShareResultView.as_view(), name="result"),
]
