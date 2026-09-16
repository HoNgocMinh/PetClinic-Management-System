from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Appointment, Clinic, MedicalRecord, Pet, Service, User


pytestmark = pytest.mark.django_db


@pytest.fixture
def medical_record_context():
    owner = User.objects.create_user(
        username="owner",
        email="owner@example.com",
        password="password123",
        full_name="Pet Owner",
    )
    other_owner = User.objects.create_user(
        username="other_owner",
        email="other-owner@example.com",
        password="password123",
        full_name="Other Owner",
    )
    clinic = Clinic.objects.create(name="Clinic A", address="123 Street")
    other_clinic = Clinic.objects.create(name="Clinic B", address="456 Street")
    staff = User.objects.create_user(
        username="staff",
        email="staff@example.com",
        password="password123",
        full_name="Clinic Staff",
        role=User.ROLE_CLINIC_STAFF,
        clinic=clinic,
    )
    other_staff = User.objects.create_user(
        username="other_staff",
        email="other-staff@example.com",
        password="password123",
        full_name="Other Clinic Staff",
        role=User.ROLE_CLINIC_STAFF,
        clinic=other_clinic,
    )
    service = Service.objects.create(
        clinic=clinic,
        name="General Exam",
        service_type=Service.SERVICE_EXAM,
        price=100000,
        duration_minutes=60,
    )
    pet = Pet.objects.create(
        owner=owner,
        name="Milu",
        species=Pet.SPECIES_DOG,
        gender=Pet.GENDER_MALE,
    )
    other_pet = Pet.objects.create(
        owner=other_owner,
        name="Mina",
        species=Pet.SPECIES_CAT,
        gender=Pet.GENDER_FEMALE,
    )

    return SimpleNamespace(
        client=APIClient(),
        owner=owner,
        other_owner=other_owner,
        clinic=clinic,
        other_clinic=other_clinic,
        staff=staff,
        other_staff=other_staff,
        service=service,
        pet=pet,
        other_pet=other_pet,
    )


def authenticate(ctx, user):
    ctx.client.force_authenticate(user=user)


def medical_record_payload():
    return {
        "symptoms": "Coughing",
        "diagnosis": "Mild respiratory infection",
        "treatment": "Rest and medication",
        "note": "Follow up in 7 days",
    }


def create_appointment(ctx, owner=None, pet=None, status_value=Appointment.STATUS_CHECKED_IN):
    return Appointment.objects.create(
        owner=owner or ctx.owner,
        pet=pet or ctx.pet,
        clinic=ctx.clinic,
        service=ctx.service,
        appointment_time=timezone.now() + timedelta(days=1),
        status=status_value,
    )


def create_medical_record(ctx, owner=None, pet=None):
    appointment = create_appointment(ctx, owner=owner, pet=pet)
    return MedicalRecord.objects.create(
        appointment=appointment,
        pet=appointment.pet,
        clinic=appointment.clinic,
        staff=ctx.staff,
        symptoms="Coughing",
        diagnosis="Mild respiratory infection",
        treatment="Rest",
        note="",
    )


def test_staff_can_create_medical_record_for_checked_in_appointment(medical_record_context):
    appointment = create_appointment(
        medical_record_context,
        status_value=Appointment.STATUS_CHECKED_IN,
    )
    authenticate(medical_record_context, medical_record_context.staff)

    response = medical_record_context.client.post(
        reverse("appointment-medical-record", kwargs={"appointment_id": appointment.id}),
        medical_record_payload(),
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["success"] is True
    assert response.data["data"]["appointment_id"] == appointment.id
    assert response.data["data"]["pet_id"] == medical_record_context.pet.id
    assert response.data["data"]["clinic_id"] == medical_record_context.clinic.id
    assert response.data["data"]["staff_id"] == medical_record_context.staff.id
    assert MedicalRecord.objects.count() == 1


def test_staff_cannot_create_medical_record_for_pending_appointment(medical_record_context):
    appointment = create_appointment(
        medical_record_context,
        status_value=Appointment.STATUS_PENDING,
    )
    authenticate(medical_record_context, medical_record_context.staff)

    response = medical_record_context.client.post(
        reverse("appointment-medical-record", kwargs={"appointment_id": appointment.id}),
        medical_record_payload(),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert MedicalRecord.objects.count() == 0


def test_staff_from_other_clinic_cannot_create_medical_record(medical_record_context):
    appointment = create_appointment(
        medical_record_context,
        status_value=Appointment.STATUS_CHECKED_IN,
    )
    authenticate(medical_record_context, medical_record_context.other_staff)

    response = medical_record_context.client.post(
        reverse("appointment-medical-record", kwargs={"appointment_id": appointment.id}),
        medical_record_payload(),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False
    assert MedicalRecord.objects.count() == 0


def test_pet_owner_can_list_medical_records_for_their_pet(medical_record_context):
    record = create_medical_record(medical_record_context)
    create_medical_record(
        medical_record_context,
        owner=medical_record_context.other_owner,
        pet=medical_record_context.other_pet,
    )
    authenticate(medical_record_context, medical_record_context.owner)

    response = medical_record_context.client.get(
        reverse("owner-pet-medical-record-list", kwargs={"pet_id": medical_record_context.pet.id}),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert len(response.data["data"]) == 1
    assert response.data["data"][0]["id"] == record.id


def test_pet_owner_cannot_get_medical_record_detail_for_another_owner_pet(
    medical_record_context,
):
    record = create_medical_record(
        medical_record_context,
        owner=medical_record_context.other_owner,
        pet=medical_record_context.other_pet,
    )
    authenticate(medical_record_context, medical_record_context.owner)

    response = medical_record_context.client.get(
        reverse("owner-medical-record-detail", kwargs={"record_id": record.id}),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False
