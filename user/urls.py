from .views import UserRegistrationView, CheckUserEmailView
from user import views
from django.urls import path


appname = "user"


urlpatterns = [
    path("sign-up", UserRegistrationView.as_view(), name="sign-up"),
    path("exist", CheckUserEmailView.as_view(), name="exist"),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
