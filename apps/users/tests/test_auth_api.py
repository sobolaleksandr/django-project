import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from conftest import PASSWORD

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_register_creates_user(api_client):
    payload = {
        "username": "newbie",
        "email": "newbie@example.com",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
    }

    response = api_client.post(reverse("register"), payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == "newbie"
    assert "password" not in response.data
    created = User.objects.get(username="newbie")
    assert created.check_password(PASSWORD)


def test_register_rejects_password_mismatch(api_client):
    payload = {
        "username": "newbie",
        "email": "newbie@example.com",
        "password": PASSWORD,
        "password_confirm": "OtherPassw0rd!",
    }

    response = api_client.post(reverse("register"), payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password_confirm" in response.data


def test_register_rejects_weak_password(api_client):
    payload = {
        "username": "newbie",
        "email": "newbie@example.com",
        "password": "12345",
        "password_confirm": "12345",
    }

    response = api_client.post(reverse("register"), payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data


def test_register_rejects_duplicate_email(api_client, user):
    payload = {
        "username": "another",
        "email": user.email,
        "password": PASSWORD,
        "password_confirm": PASSWORD,
    }

    response = api_client.post(reverse("register"), payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


def test_obtain_and_use_token(api_client, user):
    response = api_client.post(
        reverse("token_obtain_pair"),
        {"username": user.username, "password": PASSWORD},
    )

    assert response.status_code == status.HTTP_200_OK
    access = response.data["access"]

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    me_response = api_client.get(reverse("user-me"))

    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.data["username"] == user.username


def test_refresh_token(api_client, user):
    tokens = api_client.post(
        reverse("token_obtain_pair"),
        {"username": user.username, "password": PASSWORD},
    ).data

    response = api_client.post(reverse("token_refresh"), {"refresh": tokens["refresh"]})

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


def test_obtain_token_with_wrong_password(api_client, user):
    response = api_client.post(
        reverse("token_obtain_pair"),
        {"username": user.username, "password": "wrong-password"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_anonymous_access_is_forbidden(api_client):
    response = api_client.get(reverse("task-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
