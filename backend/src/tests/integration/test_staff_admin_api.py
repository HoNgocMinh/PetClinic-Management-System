from types import SimpleNamespace

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Clinic, User


pytestmark = pytest.mark.django_db


@pytest.fixture
def staff_admin_context():
    clinic = Clinic.objects.create(name="Clinic A", address="123 Street")
    other_clinic = Clinic.objects.create(name="Clinic B", address="456 Street")
    return SimpleNamespace(
        client=APIClient(),
        clinic=clinic,
        other_clinic=other_clinic,
        admin=User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            full_name="Admin User",
            role=User.ROLE_ADMIN,
        ),
        owner=User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="password123",
            full_name="Pet Owner",
        ),
    )


def authenticate(ctx, user):
    ctx.client.force_authenticate(user=user)


def staff_payload(ctx, **overrides):
    payload = {
        "username": "staff",
        "email": "staff@example.com",
        "password": "StrongStaffPass123!",
        "full_name": "Clinic Staff",
        "phone": "0900000000",
        "address": "123 Street",
        "clinic_id": ctx.clinic.id,
        "is_active": True,
    }
    payload.update(overrides)
    return payload


def test_admin_can_manage_staff_lifecycle(staff_admin_context):
    authenticate(staff_admin_context, staff_admin_context.admin)

    create_response = staff_admin_context.client.post(
        reverse("admin-staff-list-create"),
        staff_payload(staff_admin_context),
        format="json",
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    staff_id = create_response.data["data"]["id"]

    list_response = staff_admin_context.client.get(
        reverse("admin-staff-list-create"),
        {"clinic_id": staff_admin_context.clinic.id, "is_active": "true"},
    )
    detail_response = staff_admin_context.client.get(
        reverse("admin-staff-detail", kwargs={"staff_id": staff_id}),
    )
    update_response = staff_admin_context.client.put(
        reverse("admin-staff-detail", kwargs={"staff_id": staff_id}),
        {
            "email": "staff-updated@example.com",
            "password": "AnotherStaffPass123!",
            "full_name": "Updated Staff",
            "phone": "0911111111",
            "address": "Updated Street",
            "clinic_id": staff_admin_context.other_clinic.id,
            "is_active": True,
        },
        format="json",
    )
    delete_response = staff_admin_context.client.delete(
        reverse("admin-staff-detail", kwargs={"staff_id": staff_id}),
    )

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["data"]) == 1
    assert detail_response.status_code == status.HTTP_200_OK
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data["data"]["email"] == "staff-updated@example.com"
    assert update_response.data["data"]["clinic_id"] == staff_admin_context.other_clinic.id
    assert delete_response.status_code == status.HTTP_200_OK
    assert User.objects.get(id=staff_id).is_active is False


def test_admin_staff_list_rejects_invalid_clinic_id_filter(staff_admin_context):
    authenticate(staff_admin_context, staff_admin_context.admin)

    response = staff_admin_context.client.get(
        reverse("admin-staff-list-create"),
        {"clinic_id": "abc"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False


def test_create_staff_rejects_unknown_clinic(staff_admin_context):
    authenticate(staff_admin_context, staff_admin_context.admin)

    response = staff_admin_context.client.post(
        reverse("admin-staff-list-create"),
        staff_payload(staff_admin_context, clinic_id=999999),
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["success"] is False


def test_non_admin_cannot_manage_staff(staff_admin_context):
    authenticate(staff_admin_context, staff_admin_context.owner)

    response = staff_admin_context.client.post(
        reverse("admin-staff-list-create"),
        staff_payload(staff_admin_context),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False
