from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="Re:forming U, MZ?",
        default_version="v2",
        description="Re:forming U, MZ? 프로젝트 API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    urlconf="rumz.urls",
    url="https://rumz.site"
)

urlpatterns = [
    path("api/", include("django_prometheus.urls")),
    re_path(
        r"^api/swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^api/swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^api/redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc-v1",
    ),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/admin/", admin.site.urls),
    path("api/users/", include("user.urls")),
    path("api/apps/", include("chat.urls")),
    path("api/gpts/", include("gpt.urls")),
    path("api/share/", include("share.urls")),
]
