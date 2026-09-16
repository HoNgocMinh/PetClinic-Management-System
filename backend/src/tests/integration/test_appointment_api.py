from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Appointment, Clinic, Pet, Service, User


pytestmark = pytest.mark.django_db


@pytest.fixture
def appointment_context():
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


def appointment_payload(ctx, appointment_time=None):
    return {
        "pet_id": ctx.pet.id,
        "clinic_id": ctx.clinic.id,
        "service_id": ctx.service.id,
        "appointment_time": appointment_time or timezone.now() + timedelta(days=1),
        "note": "Regular checkup",
    }


def create_appointment(ctx, owner=None, pet=None, appointment_time=None):
    return Appointment.objects.create(
        owner=owner or ctx.owner,
        pet=pet or ctx.pet,
        clinic=ctx.clinic,
        service=ctx.service,
        appointment_time=appointment_time or timezone.now() + timedelta(days=1),
        status=Appointment.STATUS_PENDING,
    )


def test_pet_owner_can_create_appointment(appointment_context):
    authenticate(appointment_context, appointment_context.owner)

    response = appointment_context.client.post(
        reverse("appointment-list-create"),
        appointment_payload(appointment_context),
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["success"] is True
    assert response.data["data"]["owner"] == appointment_context.owner.id
    assert response.data["data"]["pet"] == appointment_context.pet.id
    assert response.data["data"]["status"] == Appointment.STATUS_PENDING
    assert Appointment.objects.count() == 1


def test_pet_owner_cannot_create_appointment_with_time_conflict(appointment_context):
    appointment_time = timezone.now() + timedelta(days=1)
    create_appointment(appointment_context, appointment_time=appointment_time)
    authenticate(appointment_context, appointment_context.owner)

    response = appointment_context.client.post(
        reverse("appointment-list-create"),
        appointment_payload(
            appointment_context,
            appointment_time=appointment_time + timedelta(minutes=30),
        ),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert Appointment.objects.count() == 1


def test_staff_can_confirm_appointment_in_same_clinic(appointment_context):
    appointment = create_appointment(appointment_context)
    authenticate(appointment_context, appointment_context.staff)

    response = appointment_context.client.post(
        reverse("appointment-confirm", kwargs={"appointment_id": appointment.id}),
        format="json",
    )

    appointment.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert response.data["data"]["status"] == Appointment.STATUS_CONFIRMED
    assert appointment.status == Appointment.STATUS_CONFIRMED


def test_staff_from_other_clinic_cannot_confirm_appointment(appointment_context):
    appointment = create_appointment(appointment_context)
    authenticate(appointment_context, appointment_context.other_staff)

    response = appointment_context.client.post(
        reverse("appointment-confirm", kwargs={"appointment_id": appointment.id}),
        format="json",
    )

    appointment.refresh_from_db()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False
    assert appointment.status == Appointment.STATUS_PENDING


def test_pet_owner_can_list_only_their_appointments(appointment_context):
    owner_appointment = create_appointment(appointment_context)
    create_appointment(
        appointment_context,
        owner=appointment_context.other_owner,
        pet=appointment_context.other_pet,
    )
    authenticate(appointment_context, appointment_context.owner)

    response = appointment_context.client.get(reverse("appointment-list-create"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert len(response.data["data"]) == 1
    assert response.data["data"][0]["id"] == owner_appointment.id


def test_pet_owner_can_view_update_and_cancel_pending_appointment(appointment_context):
    appointment = create_appointment(appointment_context)
    new_time = timezone.now() + timedelta(days=2)
    authenticate(appointment_context, appointment_context.owner)

    detail_response = appointment_context.client.get(
        reverse("appointment-detail", kwargs={"appointment_id": appointment.id}),
    )
    update_response = appointment_context.client.put(
        reverse("appointment-detail", kwargs={"appointment_id": appointment.id}),
        {
            "appointment_time": new_time,
            "note": "Updated note",
        },
        format="json",
    )
    cancel_response = appointment_context.client.delete(
        reverse("appointment-detail", kwargs={"appointment_id": appointment.id}),
    )

    appointment.refresh_from_db()
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data["data"]["id"] == appointment.id
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data["data"]["note"] == "Updated note"
    assert cancel_response.status_code == status.HTTP_200_OK
    assert appointment.status == Appointment.STATUS_CANCELLED


def test_pet_owner_cannot_view_another_owners_appointment(appointment_context):
    appointment = create_appointment(
        appointment_context,
        owner=appointment_context.other_owner,
        pet=appointment_context.other_pet,
    )
    authenticate(appointment_context, appointment_context.owner)

    response = appointment_context.client.get(
        reverse("appointment-detail", kwargs={"appointment_id": appointment.id}),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False


def test_staff_can_list_and_view_same_clinic_appointments(appointment_context):
    appointment = create_appointment(appointment_context)
    authenticate(appointment_context, appointment_context.staff)

    list_response = appointment_context.client.get(reverse("appointment-clinic-list"))
    detail_response = appointment_context.client.get(
        reverse("appointment-clinic-detail", kwargs={"appointment_id": appointment.id}),
    )

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["data"]) == 1
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data["data"]["id"] == appointment.id


def test_staff_from_other_clinic_cannot_view_clinic_appointment_detail(appointment_context):
    appointment = create_appointment(appointment_context)
    authenticate(appointment_context, appointment_context.other_staff)

    response = appointment_context.client.get(
        reverse("appointment-clinic-detail", kwargs={"appointment_id": appointment.id}),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False


def test_staff_can_move_appointment_through_api_service_flow(appointment_context):
    appointment = create_appointment(appointment_context)
    authenticate(appointment_context, appointment_context.staff)

    confirm_response = appointment_context.client.post(
        reverse("appointment-confirm", kwargs={"appointment_id": appointment.id}),
        format="json",
    )
    check_in_response = appointment_context.client.post(
        reverse("appointment-check-in", kwargs={"appointment_id": appointment.id}),
        format="json",
    )
    start_response = appointment_context.client.post(
        reverse("appointment-start", kwargs={"appointment_id": appointment.id}),
        format="json",
    )
    complete_response = appointment_context.client.post(
        reverse("appointment-complete", kwargs={"appointment_id": appointment.id}),
        format="json",
    )

    appointment.refresh_from_db()
    assert confirm_response.status_code == status.HTTP_200_OK
    assert check_in_response.status_code == status.HTTP_200_OK
    assert start_response.status_code == status.HTTP_200_OK
    assert complete_response.status_code == status.HTTP_200_OK
    assert appointment.status == Appointment.STATUS_WAITING_PAYMENT
    assert complete_response.data["data"]["payment"]["status"] == "PENDING"


def test_staff_can_mark_confirmed_appointment_as_no_show(appointment_context):
    appointment = create_appointment(appointment_context)
    appointment.status = Appointment.STATUS_CONFIRMED
    appointment.save()
    authenticate(appointment_context, appointment_context.staff)

    response = appointment_context.client.post(
        reverse("appointment-no-show", kwargs={"appointment_id": appointment.id}),
        format="json",
    )

    appointment.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert appointment.status == Appointment.STATUS_NO_SHOW
