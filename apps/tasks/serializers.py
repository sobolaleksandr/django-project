from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.tasks.models import Comment, Task
from apps.users.serializers import UserSerializer

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "task", "author", "text", "created_at", "updated_at"]
        read_only_fields = ["id", "task", "author", "created_at", "updated_at"]


class TaskSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        required=False,
        allow_null=True,
        write_only=True,
    )
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "author",
            "assignee",
            "assignee_id",
            "due_date",
            "completed_at",
            "is_overdue",
            "comments_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "completed_at", "created_at", "updated_at"]


class TaskDetailSerializer(TaskSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = [*TaskSerializer.Meta.fields, "comments"]


class TaskAssignSerializer(serializers.Serializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        allow_null=True,
    )
