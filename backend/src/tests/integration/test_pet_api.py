from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Pet, User


pytestmark = pytest.mark.django_db


@pytest.fixture
def pet_context():
    return SimpleNamespace(
        client=APIClient(),
        owner=User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="password123",
            full_name="Pet Owner",
        ),
        other_owner=User.objects.create_user(
            username="other_owner",
            email="other-owner@example.com",
            password="password123",
            full_name="Other Owner",
        ),
    )


def authenticate(ctx, user):
    ctx.client.force_authenticate(user=user)


def pet_payload(**overrides):
    payload = {
        "name": "Milu",
        "species": Pet.SPECIES_DOG,
        "breed": "Poodle",
        "gender": Pet.GENDER_MALE,
        "birth_date": "2023-01-01",
        "weight": "4.50",
        "note": "Friendly",
    }
    payload.update(overrides)
    return payload


def create_pet(ctx, owner=None, **overrides):
    data = {
        "owner": owner or ctx.owner,
        "name": "Milu",
        "species": Pet.SPECIES_DOG,
        "breed": "Poodle",
        "gender": Pet.GENDER_MALE,
        "birth_date": date(2023, 1, 1),
        "weight": "4.50",
        "note": "Friendly",
    }
    data.update(overrides)
    return Pet.objects.create(**data)


def test_owner_can_manage_pet_lifecycle(pet_context):
    authenticate(pet_context, pet_context.owner)

    create_response = pet_context.client.post(
        reverse("pet-list-create"),
        pet_payload(),
        format="json",
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    assert create_response.data["success"] is True
    pet_id = create_response.data["data"]["id"]

    list_response = pet_context.client.get(reverse("pet-list-create"))
    detail_response = pet_context.client.get(reverse("pet-detail", kwargs={"pet_id": pet_id}))
    update_response = pet_context.client.put(
        reverse("pet-detail", kwargs={"pet_id": pet_id}),
        pet_payload(name="Milu Updated", weight="5.25"),
        format="json",
    )
    delete_response = pet_context.client.delete(reverse("pet-detail", kwargs={"pet_id": pet_id}))

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["data"]) == 1
    assert detail_response.status_code == status.HTTP_200_OK
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data["data"]["name"] == "Milu Updated"
    assert delete_response.status_code == status.HTTP_200_OK
    assert Pet.objects.get(id=pet_id).is_active is False


def test_owner_cannot_access_another_owners_pet(pet_context):
    pet = create_pet(pet_context, owner=pet_context.other_owner)
    authenticate(pet_context, pet_context.owner)

    response = pet_context.client.get(reverse("pet-detail", kwargs={"pet_id": pet.id}))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False


def test_create_pet_rejects_invalid_birth_date_and_weight(pet_context):
    authenticate(pet_context, pet_context.owner)

    future_birth_date_response = pet_context.client.post(
        reverse("pet-list-create"),
        pet_payload(birth_date=str(date.today() + timedelta(days=1))),
        format="json",
    )
    invalid_weight_response = pet_context.client.post(
        reverse("pet-list-create"),
        pet_payload(weight="0"),
        format="json",
    )

    assert future_birth_date_response.status_code == status.HTTP_400_BAD_REQUEST
    assert future_birth_date_response.data["success"] is False
    assert invalid_weight_response.status_code == status.HTTP_400_BAD_REQUEST
    assert invalid_weight_response.data["success"] is False
