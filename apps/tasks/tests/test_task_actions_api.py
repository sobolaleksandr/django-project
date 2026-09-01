import pytest
from django.urls import reverse
from rest_framework import status

from apps.tasks.models import Task
from apps.tasks.tests.factories import TaskFactory

pytestmark = pytest.mark.django_db


def test_author_assigns_task_to_another_user(auth_client, task, other_user):
    response = auth_client.post(
        reverse("task-assign", args=[task.id]),
        {"assignee_id": other_user.id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["assignee"]["id"] == other_user.id
    task.refresh_from_db()
    assert task.assignee_id == other_user.id


def test_assign_accepts_null_to_unassign(auth_client, user, other_user):
    task = TaskFactory(author=user, assignee=other_user)

    response = auth_client.post(reverse("task-assign", args=[task.id]), {"assignee_id": None})

    assert response.status_code == status.HTTP_200_OK
    task.refresh_from_db()
    assert task.assignee is None


def test_assign_rejects_unknown_user(auth_client, task):
    response = auth_client.post(reverse("task-assign", args=[task.id]), {"assignee_id": 999999})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "assignee_id" in response.data


def test_stranger_cannot_assign_task(other_client, task, other_user):
    response = other_client.post(
        reverse("task-assign", args=[task.id]),
        {"assignee_id": other_user.id},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_author_completes_task(auth_client, task):
    response = auth_client.post(reverse("task-complete", args=[task.id]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == Task.Status.DONE
    assert response.data["completed_at"] is not None
    task.refresh_from_db()
    assert task.is_completed is True


def test_assignee_completes_task(other_client, user, other_user):
    task = TaskFactory(author=user, assignee=other_user)

    response = other_client.post(reverse("task-complete", args=[task.id]))

    assert response.status_code == status.HTTP_200_OK
    task.refresh_from_db()
    assert task.status == Task.Status.DONE


def test_stranger_cannot_complete_task(other_client, task):
    response = other_client.post(reverse("task-complete", args=[task.id]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    task.refresh_from_db()
    assert task.status == Task.Status.TODO


def test_reopen_clears_completed_at(auth_client, task):
    auth_client.post(reverse("task-complete", args=[task.id]))

    response = auth_client.post(reverse("task-reopen", args=[task.id]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == Task.Status.IN_PROGRESS
    assert response.data["completed_at"] is None


def test_stranger_cannot_reopen_task(other_client, auth_client, task):
    auth_client.post(reverse("task-complete", args=[task.id]))

    response = other_client.post(reverse("task-reopen", args=[task.id]))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_complete_requires_authentication(api_client, task):
    response = api_client.post(reverse("task-complete", args=[task.id]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
