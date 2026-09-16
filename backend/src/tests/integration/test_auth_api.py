from types import SimpleNamespace

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models import User


pytestmark = pytest.mark.django_db


@pytest.fixture
def auth_context():
    password = "StrongPass123!"
    user = User.objects.create_user(
        username="owner",
        email="owner@example.com",
        password=password,
        full_name="Pet Owner",
    )
    return SimpleNamespace(client=APIClient(), password=password, user=user)


def login(ctx, username="owner", password=None):
    return ctx.client.post(
        reverse("login"),
        {
            "username": username,
            "password": password or ctx.password,
        },
        format="json",
    )


def test_register_creates_pet_owner_user(auth_context):
    response = auth_context.client.post(
        reverse("register"),
        {
            "username": "new_owner",
            "email": "new-owner@example.com",
            "password": "AnotherStrongPass123!",
            "full_name": "New Pet Owner",
            "phone": "0900000000",
            "address": "123 Street",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["success"] is True
    assert response.data["data"]["username"] == "new_owner"
    assert response.data["data"]["role"] == User.ROLE_PET_OWNER
    assert "password" not in response.data["data"]
    assert User.objects.filter(username="new_owner").exists()


def test_login_returns_tokens_and_user_data(auth_context):
    response = login(auth_context)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert "access_token" in response.data["data"]
    assert "refresh_token" in response.data["data"]
    assert response.data["data"]["user"]["username"] == auth_context.user.username


def test_profile_without_token_is_rejected(auth_context):
    response = auth_context.client.get(reverse("profile"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["success"] is False


def test_profile_with_access_token_returns_current_user(auth_context):
    login_response = login(auth_context)
    access_token = login_response.data["data"]["access_token"]
    auth_context.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = auth_context.client.get(reverse("profile"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert response.data["data"]["id"] == auth_context.user.id
    assert response.data["data"]["username"] == auth_context.user.username


def test_change_password_updates_login_credentials(auth_context):
    login_response = login(auth_context)
    access_token = login_response.data["data"]["access_token"]
    auth_context.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = auth_context.client.put(
        reverse("change-password"),
        {
            "old_password": auth_context.password,
            "new_password": "NewStrongPass123!",
            "confirm_password": "NewStrongPass123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True

    auth_context.client.credentials()
    old_login_response = login(auth_context)
    assert old_login_response.status_code == status.HTTP_401_UNAUTHORIZED

    new_login_response = login(auth_context, password="NewStrongPass123!")
    assert new_login_response.status_code == status.HTTP_200_OK
    assert "access_token" in new_login_response.data["data"]


def test_change_password_rejects_wrong_current_password(auth_context):
    login_response = login(auth_context)
    access_token = login_response.data["data"]["access_token"]
    auth_context.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = auth_context.client.put(
        reverse("change-password"),
        {
            "old_password": "WrongPass123!",
            "new_password": "NewStrongPass123!",
            "confirm_password": "NewStrongPass123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
