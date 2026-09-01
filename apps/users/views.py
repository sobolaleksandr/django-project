from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, mixins, permissions, viewsets

from apps.users.serializers import RegisterSerializer, UserSerializer

User = get_user_model()


@extend_schema(
    tags=["auth"],
    summary="Регистрация пользователя",
    description="Создаёт нового пользователя. Доступно без авторизации.",
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    list=extend_schema(
        tags=["users"],
        summary="Список пользователей",
        description="Используется для выбора исполнителя задачи.",
    ),
    retrieve=extend_schema(tags=["users"], summary="Карточка пользователя"),
)
class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username"]


@extend_schema(
    tags=["users"],
    summary="Текущий пользователь",
    description="Возвращает профиль пользователя, которому принадлежит access-токен.",
)
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return self.request.user
