import pytest
from rest_framework.test import APIClient

from apps.tasks.tests.factories import CommentFactory, TaskFactory
from apps.users.tests.factories import UserFactory

PASSWORD = "StrongPassw0rd!"


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user():
    return UserFactory(password=PASSWORD)


@pytest.fixture
def other_user():
    return UserFactory(password=PASSWORD)


@pytest.fixture
def auth_client(api_client, user) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def other_client(api_client, other_user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=other_user)
    return client


@pytest.fixture
def task(user):
    return TaskFactory(author=user)


@pytest.fixture
def comment(task, user):
    return CommentFactory(task=task, author=user)
