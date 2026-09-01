from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.tasks.models import Task


class IsAuthorOrReadOnly(permissions.BasePermission):
    message = "Изменять и удалять объект может только его автор."

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == request.user.id


class IsAuthorOrAssignee(permissions.BasePermission):
    message = "Менять статус задачи может только её автор или назначенный исполнитель."

    def has_object_permission(self, request: Request, view: APIView, obj: Task) -> bool:
        return request.user.id in (obj.author_id, obj.assignee_id)
