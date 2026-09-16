from types import SimpleNamespace

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Clinic, Service, User


pytestmark = pytest.mark.django_db


@pytest.fixture
def clinic_context():
    return SimpleNamespace(
        client=APIClient(),
        admin=User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            full_name="Admin User",
            role=User.ROLE_ADMIN,
        ),
    )


def authenticate(ctx, user):
    ctx.client.force_authenticate(user=user)


def clinic_payload(**overrides):
    payload = {
        "name": "Clinic A",
        "address": "123 Street",
        "phone": "0900000000",
        "email": "clinic-a@example.com",
    }
    payload.update(overrides)
    return payload


def service_payload(clinic_id, **overrides):
    payload = {
        "clinic_id": clinic_id,
        "name": "General Exam",
        "service_type": Service.SERVICE_EXAM,
        "description": "Regular checkup",
        "price": "100000.00",
        "duration_minutes": 60,
    }
    payload.update(overrides)
    return payload


def test_public_can_list_and_view_active_clinics(clinic_context):
    active_clinic = Clinic.objects.create(name="Clinic A", address="123 Street")
    inactive_clinic = Clinic.objects.create(
        name="Clinic B",
        address="456 Street",
        is_active=False,
    )

    list_response = clinic_context.client.get(reverse("clinic-list-create"))
    detail_response = clinic_context.client.get(
        reverse("clinic-detail", kwargs={"clinic_id": active_clinic.id}),
    )
    inactive_detail_response = clinic_context.client.get(
        reverse("clinic-detail", kwargs={"clinic_id": inactive_clinic.id}),
    )

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["data"]) == 1
    assert list_response.data["data"][0]["id"] == active_clinic.id
    assert detail_response.status_code == status.HTTP_200_OK
    assert inactive_detail_response.status_code == status.HTTP_400_BAD_REQUEST


def test_admin_can_manage_clinic_lifecycle(clinic_context):
    authenticate(clinic_context, clinic_context.admin)

    create_response = clinic_context.client.post(
        reverse("clinic-list-create"),
        clinic_payload(),
        format="json",
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    clinic_id = create_response.data["data"]["id"]

    update_response = clinic_context.client.put(
        reverse("clinic-detail", kwargs={"clinic_id": clinic_id}),
        clinic_payload(name="Clinic Updated", address="Updated Street"),
        format="json",
    )
    delete_response = clinic_context.client.delete(
        reverse("clinic-detail", kwargs={"clinic_id": clinic_id}),
    )

    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data["data"]["name"] == "Clinic Updated"
    assert delete_response.status_code == status.HTTP_200_OK
    assert Clinic.objects.get(id=clinic_id).is_active is False


def test_admin_can_manage_service_lifecycle(clinic_context):
    clinic = Clinic.objects.create(name="Clinic A", address="123 Street")
    authenticate(clinic_context, clinic_context.admin)

    create_response = clinic_context.client.post(
        reverse("service-create"),
        service_payload(clinic.id),
        format="json",
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    service_id = create_response.data["data"]["id"]

    list_response = clinic_context.client.get(
        reverse("service-by-clinic", kwargs={"clinic_id": clinic.id}),
    )
    update_response = clinic_context.client.put(
        reverse("service-update-delete", kwargs={"service_id": service_id}),
        {
            "name": "General Exam Updated",
            "service_type": Service.SERVICE_OTHER,
            "description": "Updated",
            "price": "120000.00",
            "duration_minutes": 45,
            "is_active": True,
        },
        format="json",
    )
    delete_response = clinic_context.client.delete(
        reverse("service-update-delete", kwargs={"service_id": service_id}),
    )

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["data"]) == 1
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data["data"]["name"] == "General Exam Updated"
    assert delete_response.status_code == status.HTTP_200_OK
    assert Service.objects.get(id=service_id).is_active is False


def test_service_validation_rejects_invalid_price_and_duration(clinic_context):
    clinic = Clinic.objects.create(name="Clinic A", address="123 Street")
    authenticate(clinic_context, clinic_context.admin)

    invalid_price_response = clinic_context.client.post(
        reverse("service-create"),
        service_payload(clinic.id, price="0.00"),
        format="json",
    )
    invalid_duration_response = clinic_context.client.post(
        reverse("service-create"),
        service_payload(clinic.id, duration_minutes=0),
        format="json",
    )

    assert invalid_price_response.status_code == status.HTTP_400_BAD_REQUEST
    assert invalid_price_response.data["success"] is False
    assert invalid_duration_response.status_code == status.HTTP_400_BAD_REQUEST
    assert invalid_duration_response.data["success"] is False
