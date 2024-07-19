from user import views
from django.urls import path


appname = "user"


urlpatterns = [
    path("sign-up", views.UserRegistrationView.as_view(), name="sign-up"),
    path("exists", views.CheckUserEmailView.as_view(), name="exist"),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('results', views.UserResultView.as_view(), name='result'),
    path('results/<int:room_id>', views.UserDetailResultView.as_view(), name='result-detail'),
]
