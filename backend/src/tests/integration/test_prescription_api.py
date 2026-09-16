from types import SimpleNamespace

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Prescription, PrescriptionItem
from src.tests.factories import (
    ClinicFactory,
    MedicalRecordFactory,
    MedicineFactory,
    PrescriptionFactory,
    PrescriptionItemFactory,
    StaffUserFactory,
    UserFactory,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def prescription_context():
    clinic = ClinicFactory()
    other_clinic = ClinicFactory()
    owner = UserFactory()
    other_owner = UserFactory()
    staff = StaffUserFactory(clinic=clinic)
    other_staff = StaffUserFactory(clinic=other_clinic)
    medical_record = MedicalRecordFactory(
        appointment__owner=owner,
        appointment__clinic=clinic,
        staff=staff,
    )
    return SimpleNamespace(
        client=APIClient(),
        clinic=clinic,
        other_clinic=other_clinic,
        owner=owner,
        other_owner=other_owner,
        staff=staff,
        other_staff=other_staff,
        medical_record=medical_record,
    )


def authenticate(ctx, user):
    ctx.client.force_authenticate(user=user)


def prescription_payload(**overrides):
    payload = {
        "note": "Take medicine after meals",
    }
    payload.update(overrides)
    return payload


def prescription_item_payload(medicine_id, **overrides):
    payload = {
        "medicine_id": medicine_id,
        "quantity": 2,
        "dosage": "1 tablet",
        "frequency": "Twice daily",
        "duration_days": 5,
        "instruction": "After meal",
    }
    payload.update(overrides)
    return payload


def create_prescription(ctx, **overrides):
    data = {
        "medical_record": ctx.medical_record,
        "clinic": ctx.clinic,
        "staff": ctx.staff,
    }
    data.update(overrides)
    return PrescriptionFactory(**data)


def test_staff_can_create_and_get_prescription_for_medical_record(prescription_context):
    authenticate(prescription_context, prescription_context.staff)

    create_response = prescription_context.client.post(
        reverse(
            "medical-record-prescription",
            kwargs={"medical_record_id": prescription_context.medical_record.id},
        ),
        prescription_payload(),
        format="json",
    )
    get_response = prescription_context.client.get(
        reverse(
            "medical-record-prescription",
            kwargs={"medical_record_id": prescription_context.medical_record.id},
        ),
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    assert create_response.data["success"] is True
    assert create_response.data["data"]["medical_record_id"] == prescription_context.medical_record.id
    assert create_response.data["data"]["clinic_id"] == prescription_context.clinic.id
    assert create_response.data["data"]["staff_id"] == prescription_context.staff.id

    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.data["success"] is True
    assert get_response.data["data"]["id"] == create_response.data["data"]["id"]


def test_staff_cannot_create_duplicate_prescription_for_medical_record(prescription_context):
    create_prescription(prescription_context)
    authenticate(prescription_context, prescription_context.staff)

    response = prescription_context.client.post(
        reverse(
            "medical-record-prescription",
            kwargs={"medical_record_id": prescription_context.medical_record.id},
        ),
        prescription_payload(),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert Prescription.objects.filter(
        medical_record=prescription_context.medical_record,
    ).count() == 1


def test_staff_from_other_clinic_cannot_create_prescription(prescription_context):
    authenticate(prescription_context, prescription_context.other_staff)

    response = prescription_context.client.post(
        reverse(
            "medical-record-prescription",
            kwargs={"medical_record_id": prescription_context.medical_record.id},
        ),
        prescription_payload(),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False
    assert Prescription.objects.count() == 0


def test_staff_can_get_and_update_prescription_detail(prescription_context):
    prescription = create_prescription(prescription_context, note="Old note")
    authenticate(prescription_context, prescription_context.staff)

    detail_response = prescription_context.client.get(
        reverse("prescription-detail", kwargs={"prescription_id": prescription.id}),
    )
    update_response = prescription_context.client.put(
        reverse("prescription-detail", kwargs={"prescription_id": prescription.id}),
        prescription_payload(note="Updated note"),
        format="json",
    )

    prescription.refresh_from_db()
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data["data"]["id"] == prescription.id
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data["data"]["note"] == "Updated note"
    assert prescription.note == "Updated note"


def test_staff_from_other_clinic_cannot_get_prescription_detail(prescription_context):
    prescription = create_prescription(prescription_context)
    authenticate(prescription_context, prescription_context.other_staff)

    response = prescription_context.client.get(
        reverse("prescription-detail", kwargs={"prescription_id": prescription.id}),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False


def test_staff_can_add_update_and_delete_prescription_item(prescription_context):
    prescription = create_prescription(prescription_context)
    medicine = MedicineFactory(clinic=prescription_context.clinic, stock_quantity=10)
    authenticate(prescription_context, prescription_context.staff)

    add_response = prescription_context.client.post(
        reverse("prescription-item-list-create", kwargs={"prescription_id": prescription.id}),
        prescription_item_payload(medicine.id, quantity=3),
        format="json",
    )
    item_id = add_response.data["data"]["id"]
    medicine.refresh_from_db()
    stock_after_add = medicine.stock_quantity

    update_response = prescription_context.client.put(
        reverse("prescription-item-detail", kwargs={"item_id": item_id}),
        {
            "quantity": 5,
            "dosage": "2 tablets",
            "frequency": "Once daily",
            "duration_days": 7,
            "instruction": "Before meal",
        },
        format="json",
    )
    medicine.refresh_from_db()
    stock_after_update = medicine.stock_quantity

    delete_response = prescription_context.client.delete(
        reverse("prescription-item-detail", kwargs={"item_id": item_id}),
    )
    medicine.refresh_from_db()
    stock_after_delete = medicine.stock_quantity

    assert add_response.status_code == status.HTTP_201_CREATED
    assert add_response.data["data"]["medicine_id"] == medicine.id
    assert stock_after_add == 7

    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data["data"]["quantity"] == 5
    assert update_response.data["data"]["dosage"] == "2 tablets"
    assert stock_after_update == 5

    assert delete_response.status_code == status.HTTP_200_OK
    assert not PrescriptionItem.objects.filter(id=item_id).exists()
    assert stock_after_delete == 10


def test_add_prescription_item_rejects_invalid_payload(prescription_context):
    prescription = create_prescription(prescription_context)
    medicine = MedicineFactory(clinic=prescription_context.clinic, stock_quantity=10)
    authenticate(prescription_context, prescription_context.staff)

    response = prescription_context.client.post(
        reverse("prescription-item-list-create", kwargs={"prescription_id": prescription.id}),
        prescription_item_payload(
            medicine.id,
            quantity=0,
            dosage=" ",
            frequency=" ",
            duration_days=0,
        ),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert PrescriptionItem.objects.count() == 0


def test_add_prescription_item_rejects_insufficient_stock(prescription_context):
    prescription = create_prescription(prescription_context)
    medicine = MedicineFactory(clinic=prescription_context.clinic, stock_quantity=1)
    authenticate(prescription_context, prescription_context.staff)

    response = prescription_context.client.post(
        reverse("prescription-item-list-create", kwargs={"prescription_id": prescription.id}),
        prescription_item_payload(medicine.id, quantity=2),
        format="json",
    )

    medicine.refresh_from_db()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert medicine.stock_quantity == 1
    assert PrescriptionItem.objects.count() == 0


def test_add_prescription_item_rejects_inactive_medicine(prescription_context):
    prescription = create_prescription(prescription_context)
    medicine = MedicineFactory(clinic=prescription_context.clinic, is_active=False)
    authenticate(prescription_context, prescription_context.staff)

    response = prescription_context.client.post(
        reverse("prescription-item-list-create", kwargs={"prescription_id": prescription.id}),
        prescription_item_payload(medicine.id),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False


def test_staff_from_other_clinic_cannot_add_item_to_prescription(prescription_context):
    prescription = create_prescription(prescription_context)
    medicine = MedicineFactory(clinic=prescription_context.other_clinic)
    authenticate(prescription_context, prescription_context.other_staff)

    response = prescription_context.client.post(
        reverse("prescription-item-list-create", kwargs={"prescription_id": prescription.id}),
        prescription_item_payload(medicine.id),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False
    assert PrescriptionItem.objects.count() == 0


def test_pet_owner_can_get_prescription_for_their_medical_record(prescription_context):
    prescription = create_prescription(prescription_context)
    item = PrescriptionItemFactory(
        prescription=prescription,
        medicine=MedicineFactory(clinic=prescription_context.clinic),
    )
    authenticate(prescription_context, prescription_context.owner)

    response = prescription_context.client.get(
        reverse(
            "owner-medical-record-prescription",
            kwargs={"medical_record_id": prescription_context.medical_record.id},
        ),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert response.data["data"]["id"] == prescription.id
    assert response.data["data"]["items"][0]["id"] == item.id


def test_pet_owner_cannot_get_prescription_for_another_owners_medical_record(
    prescription_context,
):
    create_prescription(prescription_context)
    authenticate(prescription_context, prescription_context.other_owner)

    response = prescription_context.client.get(
        reverse(
            "owner-medical-record-prescription",
            kwargs={"medical_record_id": prescription_context.medical_record.id},
        ),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False
