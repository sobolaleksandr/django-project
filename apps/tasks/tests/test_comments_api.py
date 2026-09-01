import pytest
from django.urls import reverse
from rest_framework import status

from apps.tasks.models import Comment
from apps.tasks.tests.factories import CommentFactory

pytestmark = pytest.mark.django_db


def test_create_comment(auth_client, user, task):
    response = auth_client.post(
        reverse("task-comments", args=[task.id]),
        {"text": "Беру задачу в работу"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["author"]["id"] == user.id
    assert response.data["task"] == task.id
    assert Comment.objects.filter(task=task, author=user).count() == 1


def test_any_authenticated_user_can_comment(other_client, other_user, task):
    response = other_client.post(reverse("task-comments", args=[task.id]), {"text": "Вопрос"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["author"]["id"] == other_user.id


def test_create_comment_requires_text(auth_client, task):
    response = auth_client.post(reverse("task-comments", args=[task.id]), {"text": ""})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "text" in response.data


def test_comment_list_is_ordered_and_scoped_to_task(auth_client, task):
    CommentFactory(task=task, text="Первый")
    CommentFactory(task=task, text="Второй")
    CommentFactory(text="Из другой задачи")

    response = auth_client.get(reverse("task-comments", args=[task.id]))

    assert response.status_code == status.HTTP_200_OK
    assert [item["text"] for item in response.data["results"]] == ["Первый", "Второй"]


def test_comment_for_missing_task_returns_404(auth_client):
    response = auth_client.post(reverse("task-comments", args=[999999]), {"text": "Текст"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_author_updates_own_comment(auth_client, comment):
    response = auth_client.patch(
        reverse("comment-detail", args=[comment.id]),
        {"text": "Обновлённый текст"},
    )

    assert response.status_code == status.HTTP_200_OK
    comment.refresh_from_db()
    assert comment.text == "Обновлённый текст"


def test_stranger_cannot_update_comment(other_client, comment):
    response = other_client.patch(reverse("comment-detail", args=[comment.id]), {"text": "Правка"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    comment.refresh_from_db()
    assert comment.text != "Правка"


def test_author_deletes_own_comment(auth_client, comment):
    response = auth_client.delete(reverse("comment-detail", args=[comment.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_stranger_cannot_delete_comment(other_client, comment):
    response = other_client.delete(reverse("comment-detail", args=[comment.id]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Comment.objects.filter(pk=comment.pk).exists()


def test_comment_task_is_read_only(auth_client, comment):
    other_task_comment = CommentFactory()

    response = auth_client.patch(
        reverse("comment-detail", args=[comment.id]),
        {"task": other_task_comment.task_id},
    )

    assert response.status_code == status.HTTP_200_OK
    comment.refresh_from_db()
    assert comment.task_id != other_task_comment.task_id
