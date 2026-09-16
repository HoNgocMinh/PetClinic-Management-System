from types import SimpleNamespace

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Clinic, Medicine, User


pytestmark = pytest.mark.django_db


@pytest.fixture
def medicine_context():
    clinic = Clinic.objects.create(name="Clinic A", address="123 Street")
    other_clinic = Clinic.objects.create(name="Clinic B", address="456 Street")
    return SimpleNamespace(
        client=APIClient(),
        clinic=clinic,
        other_clinic=other_clinic,
        staff=User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password123",
            full_name="Clinic Staff",
            role=User.ROLE_CLINIC_STAFF,
            clinic=clinic,
        ),
        other_staff=User.objects.create_user(
            username="other_staff",
            email="other-staff@example.com",
            password="password123",
            full_name="Other Staff",
            role=User.ROLE_CLINIC_STAFF,
            clinic=other_clinic,
        ),
    )


def authenticate(ctx, user):
    ctx.client.force_authenticate(user=user)


def medicine_payload(**overrides):
    payload = {
        "name": "Amoxicillin",
        "unit": "tablet",
        "description": "Antibiotic",
        "stock_quantity": 10,
        "price": "5000.00",
    }
    payload.update(overrides)
    return payload


def create_medicine(ctx, clinic=None, **overrides):
    data = {
        "clinic": clinic or ctx.clinic,
        "name": "Amoxicillin",
        "unit": "tablet",
        "description": "Antibiotic",
        "stock_quantity": 10,
        "price": "5000.00",
        "is_active": True,
    }
    data.update(overrides)
    return Medicine.objects.create(**data)


def test_staff_can_manage_medicine_lifecycle(medicine_context):
    authenticate(medicine_context, medicine_context.staff)

    create_response = medicine_context.client.post(
        reverse("medicine-list-create"),
        medicine_payload(),
        format="json",
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    medicine_id = create_response.data["data"]["id"]

    list_response = medicine_context.client.get(reverse("medicine-list-create"))
    detail_response = medicine_context.client.get(
        reverse("medicine-detail", kwargs={"medicine_id": medicine_id}),
    )
    update_response = medicine_context.client.put(
        reverse("medicine-detail", kwargs={"medicine_id": medicine_id}),
        {
            "name": "Amoxicillin Updated",
            "unit": "capsule",
            "description": "Updated antibiotic",
            "stock_quantity": 12,
            "price": "6000.00",
            "is_active": True,
        },
        format="json",
    )
    delete_response = medicine_context.client.delete(
        reverse("medicine-detail", kwargs={"medicine_id": medicine_id}),
    )

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["data"]) == 1
    assert detail_response.status_code == status.HTTP_200_OK
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data["data"]["name"] == "Amoxicillin Updated"
    assert delete_response.status_code == status.HTTP_200_OK
    assert Medicine.objects.get(id=medicine_id).is_active is False


def test_create_medicine_reactivates_inactive_existing_record(medicine_context):
    medicine = create_medicine(medicine_context, is_active=False)
    authenticate(medicine_context, medicine_context.staff)

    response = medicine_context.client.post(
        reverse("medicine-list-create"),
        medicine_payload(stock_quantity=20, price="7000.00"),
        format="json",
    )

    medicine.refresh_from_db()
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["data"]["id"] == medicine.id
    assert medicine.is_active is True
    assert medicine.stock_quantity == 20


def test_create_medicine_rejects_active_duplicate(medicine_context):
    create_medicine(medicine_context)
    authenticate(medicine_context, medicine_context.staff)

    response = medicine_context.client.post(
        reverse("medicine-list-create"),
        medicine_payload(),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False


def test_staff_cannot_access_other_clinic_medicine(medicine_context):
    medicine = create_medicine(medicine_context, clinic=medicine_context.other_clinic)
    authenticate(medicine_context, medicine_context.staff)

    response = medicine_context.client.get(
        reverse("medicine-detail", kwargs={"medicine_id": medicine.id}),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False


def test_medicine_list_rejects_invalid_status_filter(medicine_context):
    authenticate(medicine_context, medicine_context.staff)

    response = medicine_context.client.get(reverse("medicine-list-create"), {"status": "archived"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
