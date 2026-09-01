import pytest
from django.urls import reverse
from rest_framework import status

from apps.tasks.models import Task
from apps.tasks.tests.factories import CommentFactory, TaskFactory

pytestmark = pytest.mark.django_db


def test_create_task_sets_author_from_token(auth_client, user, other_user):
    payload = {
        "title": "Подготовить отчёт",
        "description": "Отчёт за квартал",
        "priority": Task.Priority.HIGH,
        "assignee_id": other_user.id,
    }

    response = auth_client.post(reverse("task-list"), payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["author"]["id"] == user.id
    assert response.data["assignee"]["id"] == other_user.id
    assert response.data["status"] == Task.Status.TODO


def test_create_task_requires_title(auth_client):
    response = auth_client.post(reverse("task-list"), {"description": "Без названия"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "title" in response.data


def test_create_task_with_unknown_assignee(auth_client):
    payload = {"title": "Задача", "assignee_id": 999999}

    response = auth_client.post(reverse("task-list"), payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "assignee_id" in response.data


def test_task_list_is_visible_to_any_authenticated_user(other_client, task):
    response = other_client.get(reverse("task-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


def test_task_list_contains_comments_count(auth_client, task):
    CommentFactory.create_batch(3, task=task)

    response = auth_client.get(reverse("task-list"))

    assert response.data["results"][0]["comments_count"] == 3


def test_task_detail_contains_comments(auth_client, task):
    CommentFactory(task=task, text="Первый")

    response = auth_client.get(reverse("task-detail", args=[task.id]))

    assert response.status_code == status.HTTP_200_OK
    assert [item["text"] for item in response.data["comments"]] == ["Первый"]


def test_filter_by_status(auth_client, user):
    TaskFactory(author=user, status=Task.Status.TODO)
    TaskFactory(author=user, status=Task.Status.DONE)

    response = auth_client.get(reverse("task-list"), {"status": Task.Status.DONE})

    assert response.data["count"] == 1
    assert response.data["results"][0]["status"] == Task.Status.DONE


def test_filter_by_assignee(auth_client, user, other_user):
    TaskFactory(author=user, assignee=other_user)
    TaskFactory(author=user)

    response = auth_client.get(reverse("task-list"), {"assignee": other_user.id})

    assert response.data["count"] == 1


def test_search_by_title(auth_client, user):
    TaskFactory(author=user, title="Починить деплой")
    TaskFactory(author=user, title="Написать документацию")

    response = auth_client.get(reverse("task-list"), {"search": "деплой"})

    assert response.data["count"] == 1


def test_ordering_by_due_date(auth_client, user):
    from datetime import timedelta

    from django.utils import timezone

    late = TaskFactory(author=user, due_date=timezone.now() + timedelta(days=5))
    soon = TaskFactory(author=user, due_date=timezone.now() + timedelta(days=1))

    response = auth_client.get(reverse("task-list"), {"ordering": "due_date"})

    assert [item["id"] for item in response.data["results"]] == [soon.id, late.id]


def test_author_can_update_task(auth_client, task):
    response = auth_client.patch(
        reverse("task-detail", args=[task.id]),
        {"title": "Новое название", "status": Task.Status.IN_PROGRESS},
    )

    assert response.status_code == status.HTTP_200_OK
    task.refresh_from_db()
    assert task.title == "Новое название"
    assert task.status == Task.Status.IN_PROGRESS


def test_stranger_cannot_update_task(other_client, task):
    response = other_client.patch(reverse("task-detail", args=[task.id]), {"title": "Взлом"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    task.refresh_from_db()
    assert task.title != "Взлом"


def test_author_cannot_be_overridden(auth_client, task, other_user):
    response = auth_client.patch(
        reverse("task-detail", args=[task.id]),
        {"author": other_user.id},
    )

    assert response.status_code == status.HTTP_200_OK
    task.refresh_from_db()
    assert task.author_id != other_user.id


def test_author_can_delete_task(auth_client, task):
    response = auth_client.delete(reverse("task-detail", args=[task.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Task.objects.filter(pk=task.pk).exists()


def test_stranger_cannot_delete_task(other_client, task):
    response = other_client.delete(reverse("task-detail", args=[task.id]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Task.objects.filter(pk=task.pk).exists()


def test_missing_task_returns_404(auth_client):
    response = auth_client.get(reverse("task-detail", args=[999999]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
