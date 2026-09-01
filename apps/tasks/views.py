from django.db.models import Count, QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.tasks.filters import TaskFilter
from apps.tasks.models import Comment, Task
from apps.tasks.permissions import IsAuthorOrAssignee, IsAuthorOrReadOnly
from apps.tasks.serializers import (
    CommentSerializer,
    TaskAssignSerializer,
    TaskDetailSerializer,
    TaskSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["tasks"],
        summary="Список задач",
        description=(
            "Задачи доступны всем авторизованным пользователям. "
            "Поддерживаются фильтры, полнотекстовый поиск и сортировка."
        ),
    ),
    create=extend_schema(
        tags=["tasks"],
        summary="Создать задачу",
        description="Автором становится владелец access-токена.",
    ),
    retrieve=extend_schema(
        tags=["tasks"],
        summary="Карточка задачи",
        description="Возвращает задачу вместе со списком комментариев.",
    ),
    update=extend_schema(tags=["tasks"], summary="Полностью обновить задачу (только автор)"),
    partial_update=extend_schema(tags=["tasks"], summary="Частично обновить задачу (только автор)"),
    destroy=extend_schema(tags=["tasks"], summary="Удалить задачу (только автор)"),
)
class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority", "status"]
    ordering = ["-created_at", "-id"]

    def get_queryset(self) -> QuerySet[Task]:
        queryset = Task.objects.select_related("author", "assignee").annotate(
            comments_count=Count("comments")
        )
        if self.action == "retrieve":
            return queryset.prefetch_related("comments__author")
        return queryset

    def get_serializer_class(self):
        if self.action == "assign":
            return TaskAssignSerializer
        if self.action == "retrieve":
            return TaskDetailSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.action in {"complete", "reopen", "assign"}:
            return [permissions.IsAuthenticated(), IsAuthorOrAssignee()]
        return super().get_permissions()

    def perform_create(self, serializer: TaskSerializer) -> None:
        serializer.save(author=self.request.user)

    def _task_response(self, task: Task) -> Response:
        serializer = TaskSerializer(task, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["tasks"],
        summary="Отметить задачу выполненной",
        description=(
            "Доступно автору задачи и её исполнителю. Проставляет статус done и дату выполнения."
        ),
        request=None,
        responses={200: TaskSerializer},
    )
    @action(detail=True, methods=["post"])
    def complete(self, request: Request, pk: int | None = None) -> Response:
        task = self.get_object()
        task.mark_completed()
        return self._task_response(task)

    @extend_schema(
        tags=["tasks"],
        summary="Вернуть задачу в работу",
        description="Доступно автору задачи и её исполнителю. Сбрасывает дату выполнения.",
        request=None,
        responses={200: TaskSerializer},
    )
    @action(detail=True, methods=["post"])
    def reopen(self, request: Request, pk: int | None = None) -> Response:
        task = self.get_object()
        task.reopen()
        return self._task_response(task)

    @extend_schema(
        tags=["tasks"],
        summary="Назначить исполнителя",
        description=(
            "Доступно автору задачи и текущему исполнителю. Значение null снимает исполнителя."
        ),
        request=TaskAssignSerializer,
        responses={200: TaskSerializer},
    )
    @action(detail=True, methods=["post"])
    def assign(self, request: Request, pk: int | None = None) -> Response:
        task = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task.assignee = serializer.validated_data["assignee"]
        task.save(update_fields=["assignee", "updated_at"])
        return self._task_response(task)


@extend_schema_view(
    get=extend_schema(tags=["comments"], summary="Комментарии задачи"),
    post=extend_schema(
        tags=["comments"],
        summary="Добавить комментарий",
        description="Автором комментария становится владелец access-токена.",
    ),
)
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.select_related("author")

    def get_task(self) -> Task:
        return get_object_or_404(Task, pk=self.kwargs["task_id"])

    def get_queryset(self) -> QuerySet[Comment]:
        return super().get_queryset().filter(task=self.get_task())

    def perform_create(self, serializer: CommentSerializer) -> None:
        serializer.save(author=self.request.user, task=self.get_task())


@extend_schema_view(
    get=extend_schema(tags=["comments"], summary="Комментарий"),
    put=extend_schema(tags=["comments"], summary="Обновить комментарий (только автор)"),
    patch=extend_schema(tags=["comments"], summary="Частично обновить комментарий (только автор)"),
    delete=extend_schema(tags=["comments"], summary="Удалить комментарий (только автор)"),
)
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    queryset = Comment.objects.select_related("author", "task")
