from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.users.views import CurrentUserView, RegisterView, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

auth_urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

urlpatterns = [
    path("auth/", include(auth_urlpatterns)),
    path("users/me/", CurrentUserView.as_view(), name="user-me"),
    path("", include(router.urls)),
]
