appname = "user"
from .views import UserRegistrationView, CheckUserEmailView
from django.urls import path, include

urlpatterns = [
    path("sign-up", UserRegistrationView.as_view(), name="sign-up"),
    path("exist", CheckUserEmailView.as_view(), name="exist"),
]
