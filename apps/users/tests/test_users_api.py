import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_user_list_returns_all_users(auth_client, user, other_user):
    response = auth_client.get(reverse("user-list"))

    assert response.status_code == status.HTTP_200_OK
    usernames = [item["username"] for item in response.data["results"]]
    assert user.username in usernames
    assert other_user.username in usernames


def test_user_detail(auth_client, other_user):
    response = auth_client.get(reverse("user-detail", args=[other_user.id]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == other_user.email


def test_current_user(auth_client, user):
    response = auth_client.get(reverse("user-me"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == user.id


def test_user_search(auth_client, other_user):
    response = auth_client.get(reverse("user-list"), {"search": other_user.username})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
