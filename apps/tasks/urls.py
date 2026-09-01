from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tasks.views import CommentDetailView, CommentListCreateView, TaskViewSet

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path(
        "tasks/<int:task_id>/comments/",
        CommentListCreateView.as_view(),
        name="task-comments",
    ),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("", include(router.urls)),
]
