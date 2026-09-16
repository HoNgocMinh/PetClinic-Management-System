from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.utils import timezone

from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)
from src.models import Appointment, Payment, Pet
from src.services.appointment_service import AppointmentService
from src.tests.factories import (
    AppointmentFactory,
    ClinicFactory,
    PetFactory,
    ServiceFactory,
    StaffUserFactory,
    UserFactory,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def appointment_context():
    owner = UserFactory(username="owner", email="owner@example.com", full_name="Pet Owner")
    other_owner = UserFactory(
        username="other_owner",
        email="other-owner@example.com",
        full_name="Other Owner",
    )
    clinic = ClinicFactory(name="Clinic A", address="123 Street")
    other_clinic = ClinicFactory(name="Clinic B", address="456 Street")
    staff = StaffUserFactory(
        username="staff",
        email="staff@example.com",
        full_name="Clinic Staff",
        clinic=clinic,
    )
    other_staff = StaffUserFactory(
        username="other_staff",
        email="other-staff@example.com",
        full_name="Other Clinic Staff",
        clinic=other_clinic,
    )
    service = ServiceFactory(
        clinic=clinic,
        name="General Exam",
        price=100000,
        duration_minutes=60,
    )
    other_service = ServiceFactory(
        clinic=other_clinic,
        name="Other General Exam",
        price=100000,
        duration_minutes=60,
    )
    pet = PetFactory(owner=owner, name="Milu")
    other_pet = PetFactory(
        owner=other_owner,
        name="Mina",
        species=Pet.SPECIES_CAT,
        gender=Pet.GENDER_FEMALE,
    )

    return SimpleNamespace(
        owner=owner,
        other_owner=other_owner,
        clinic=clinic,
        other_clinic=other_clinic,
        staff=staff,
        other_staff=other_staff,
        service=service,
        other_service=other_service,
        pet=pet,
        other_pet=other_pet,
    )


def appointment_data(ctx, appointment_time=None, pet_id=None):
    return {
        "pet_id": pet_id or ctx.pet.id,
        "clinic_id": ctx.clinic.id,
        "service_id": ctx.service.id,
        "appointment_time": appointment_time or timezone.now() + timedelta(days=1),
        "note": "Regular checkup",
    }


def create_pending_appointment(
    ctx,
    appointment_time=None,
    owner=None,
    pet=None,
    clinic=None,
    service=None,
    status=Appointment.STATUS_PENDING,
):
    return AppointmentFactory(
        owner=owner or ctx.owner,
        pet=pet or ctx.pet,
        clinic=clinic or ctx.clinic,
        service=service or ctx.service,
        appointment_time=appointment_time or timezone.now() + timedelta(days=1),
        status=status,
    )


def test_create_appointment_success(appointment_context):
    appointment_time = timezone.now() + timedelta(days=1)

    appointment = AppointmentService.create_appointment(
        appointment_context.owner,
        appointment_data(appointment_context, appointment_time=appointment_time),
    )

    assert appointment.owner == appointment_context.owner
    assert appointment.pet == appointment_context.pet
    assert appointment.clinic == appointment_context.clinic
    assert appointment.service == appointment_context.service
    assert appointment.appointment_time == appointment_time
    assert appointment.status == Appointment.STATUS_PENDING


def test_create_appointment_rejects_pet_from_another_owner(appointment_context):
    with pytest.raises(NotFoundException):
        AppointmentService.create_appointment(
            appointment_context.owner,
            appointment_data(appointment_context, pet_id=appointment_context.other_pet.id),
        )


def test_create_appointment_rejects_overlapping_time_slot(appointment_context):
    appointment_time = timezone.now() + timedelta(days=1)
    create_pending_appointment(appointment_context, appointment_time=appointment_time)

    with pytest.raises(BusinessException):
        AppointmentService.create_appointment(
            appointment_context.owner,
            appointment_data(
                appointment_context,
                appointment_time=appointment_time + timedelta(minutes=30),
            ),
        )


def test_create_appointment_rejects_inactive_clinic(appointment_context):
    appointment_context.clinic.is_active = False
    appointment_context.clinic.save()

    with pytest.raises(NotFoundException):
        AppointmentService.create_appointment(
            appointment_context.owner,
            appointment_data(appointment_context),
        )


def test_create_appointment_rejects_service_from_another_clinic(appointment_context):
    with pytest.raises(NotFoundException):
        AppointmentService.create_appointment(
            appointment_context.owner,
            {
                **appointment_data(appointment_context),
                "service_id": appointment_context.other_service.id,
            },
        )


def test_get_user_appointments_returns_only_owner_appointments(appointment_context):
    owner_appointment = create_pending_appointment(appointment_context)
    create_pending_appointment(
        appointment_context,
        owner=appointment_context.other_owner,
        pet=appointment_context.other_pet,
        clinic=appointment_context.other_clinic,
        service=appointment_context.other_service,
    )

    appointments = AppointmentService.get_user_appointments(appointment_context.owner)

    assert list(appointments) == [owner_appointment]


def test_get_clinic_appointments_returns_staff_clinic_appointments(appointment_context):
    appointment = create_pending_appointment(appointment_context)
    create_pending_appointment(
        appointment_context,
        owner=appointment_context.other_owner,
        pet=appointment_context.other_pet,
        clinic=appointment_context.other_clinic,
        service=appointment_context.other_service,
    )

    appointments = AppointmentService.get_clinic_appointments(appointment_context.staff)

    assert list(appointments) == [appointment]


def test_get_clinic_appointments_requires_staff_clinic(appointment_context):
    with pytest.raises(BusinessException):
        AppointmentService.get_clinic_appointments(appointment_context.owner)


def test_get_clinic_appointment_detail_success(appointment_context):
    appointment = create_pending_appointment(appointment_context)

    result = AppointmentService.get_clinic_appointment_detail(
        appointment_context.staff,
        appointment.id,
    )

    assert result == appointment


def test_get_clinic_appointment_detail_rejects_missing_appointment(appointment_context):
    with pytest.raises(NotFoundException):
        AppointmentService.get_clinic_appointment_detail(appointment_context.staff, 999999)


def test_get_clinic_appointment_detail_rejects_other_clinic_staff(appointment_context):
    appointment = create_pending_appointment(appointment_context)

    with pytest.raises(PermissionDeniedException):
        AppointmentService.get_clinic_appointment_detail(
            appointment_context.other_staff,
            appointment.id,
        )


def test_get_appointment_detail_success(appointment_context):
    appointment = create_pending_appointment(appointment_context)

    result = AppointmentService.get_appointment_detail(
        appointment_context.owner,
        appointment.id,
    )

    assert result == appointment


def test_get_appointment_detail_rejects_missing_appointment(appointment_context):
    with pytest.raises(NotFoundException):
        AppointmentService.get_appointment_detail(appointment_context.owner, 999999)


def test_get_appointment_detail_rejects_another_owner(appointment_context):
    appointment = create_pending_appointment(
        appointment_context,
        owner=appointment_context.other_owner,
        pet=appointment_context.other_pet,
        clinic=appointment_context.other_clinic,
        service=appointment_context.other_service,
    )

    with pytest.raises(BusinessException):
        AppointmentService.get_appointment_detail(
            appointment_context.owner,
            appointment.id,
        )


def test_staff_can_move_appointment_through_service_flow(appointment_context):
    appointment = create_pending_appointment(appointment_context)

    appointment = AppointmentService.confirm_appointment(
        appointment_context.staff,
        appointment.id,
    )
    assert appointment.status == Appointment.STATUS_CONFIRMED

    appointment = AppointmentService.check_in(appointment_context.staff, appointment.id)
    assert appointment.status == Appointment.STATUS_CHECKED_IN

    appointment = AppointmentService.start_appointment(appointment_context.staff, appointment.id)
    assert appointment.status == Appointment.STATUS_IN_PROGRESS

    appointment = AppointmentService.complete_appointment(
        appointment_context.staff,
        appointment.id,
    )
    assert appointment.status == Appointment.STATUS_WAITING_PAYMENT
    assert appointment.payment.status == Payment.STATUS_PENDING


def test_staff_from_other_clinic_cannot_confirm_appointment(appointment_context):
    appointment = create_pending_appointment(appointment_context)

    with pytest.raises(PermissionDeniedException):
        AppointmentService.confirm_appointment(appointment_context.other_staff, appointment.id)


def test_staff_from_other_clinic_cannot_check_in_appointment(appointment_context):
    appointment = create_pending_appointment(appointment_context)
    appointment.status = Appointment.STATUS_CONFIRMED
    appointment.save()

    with pytest.raises(PermissionDeniedException):
        AppointmentService.check_in(appointment_context.other_staff, appointment.id)


def test_check_in_requires_confirmed_appointment(appointment_context):
    appointment = create_pending_appointment(appointment_context)

    with pytest.raises(BusinessException):
        AppointmentService.check_in(appointment_context.staff, appointment.id)


def test_owner_cannot_update_confirmed_appointment(appointment_context):
    appointment = create_pending_appointment(appointment_context)
    appointment.status = Appointment.STATUS_CONFIRMED
    appointment.save()

    with pytest.raises(BusinessException):
        AppointmentService.update_appointment(
            appointment_context.owner,
            appointment.id,
            {"note": "Updated note"},
        )


def test_owner_can_update_pending_appointment(appointment_context):
    appointment = create_pending_appointment(appointment_context)
    new_time = timezone.now() + timedelta(days=2)

    updated_appointment = AppointmentService.update_appointment(
        appointment_context.owner,
        appointment.id,
        {
            "appointment_time": new_time,
            "note": "Updated note",
        },
    )

    assert updated_appointment.appointment_time == new_time
    assert updated_appointment.note == "Updated note"


def test_owner_update_rejects_time_conflict(appointment_context):
    appointment = create_pending_appointment(
        appointment_context,
        appointment_time=timezone.now() + timedelta(days=2),
    )
    conflicting_time = timezone.now() + timedelta(days=3)
    create_pending_appointment(appointment_context, appointment_time=conflicting_time)

    with pytest.raises(BusinessException):
        AppointmentService.update_appointment(
            appointment_context.owner,
            appointment.id,
            {"appointment_time": conflicting_time + timedelta(minutes=30)},
        )


def test_update_appointment_rejects_missing_appointment(appointment_context):
    with pytest.raises(NotFoundException):
        AppointmentService.update_appointment(
            appointment_context.owner,
            999999,
            {"note": "Updated note"},
        )


def test_update_appointment_rejects_another_owner(appointment_context):
    appointment = create_pending_appointment(
        appointment_context,
        owner=appointment_context.other_owner,
        pet=appointment_context.other_pet,
        clinic=appointment_context.other_clinic,
        service=appointment_context.other_service,
    )

    with pytest.raises(BusinessException):
        AppointmentService.update_appointment(
            appointment_context.owner,
            appointment.id,
            {"note": "Updated note"},
        )


def test_owner_cannot_cancel_confirmed_appointment(appointment_context):
    appointment = create_pending_appointment(appointment_context)
    appointment.status = Appointment.STATUS_CONFIRMED
    appointment.save()

    with pytest.raises(BusinessException):
        AppointmentService.cancel_appointment(appointment_context.owner, appointment.id)


def test_owner_can_cancel_pending_appointment(appointment_context):
    appointment = create_pending_appointment(appointment_context)

    cancelled_appointment = AppointmentService.cancel_appointment(
        appointment_context.owner,
        appointment.id,
    )

    assert cancelled_appointment.status == Appointment.STATUS_CANCELLED


def test_cancel_appointment_rejects_missing_appointment(appointment_context):
    with pytest.raises(NotFoundException):
        AppointmentService.cancel_appointment(appointment_context.owner, 999999)


def test_cancel_appointment_rejects_another_owner(appointment_context):
    appointment = create_pending_appointment(
        appointment_context,
        owner=appointment_context.other_owner,
        pet=appointment_context.other_pet,
        clinic=appointment_context.other_clinic,
        service=appointment_context.other_service,
    )

    with pytest.raises(BusinessException):
        AppointmentService.cancel_appointment(appointment_context.owner, appointment.id)


def test_confirm_requires_pending_appointment(appointment_context):
    appointment = create_pending_appointment(
        appointment_context,
        status=Appointment.STATUS_CONFIRMED,
    )

    with pytest.raises(BusinessException):
        AppointmentService.confirm_appointment(appointment_context.staff, appointment.id)


def test_start_requires_checked_in_appointment(appointment_context):
    appointment = create_pending_appointment(
        appointment_context,
        status=Appointment.STATUS_CONFIRMED,
    )

    with pytest.raises(BusinessException):
        AppointmentService.start_appointment(appointment_context.staff, appointment.id)


def test_complete_requires_in_progress_appointment(appointment_context):
    appointment = create_pending_appointment(
        appointment_context,
        status=Appointment.STATUS_CONFIRMED,
    )

    with pytest.raises(BusinessException):
        AppointmentService.complete_appointment(appointment_context.staff, appointment.id)


def test_mark_no_show_success(appointment_context):
    appointment = create_pending_appointment(
        appointment_context,
        status=Appointment.STATUS_CONFIRMED,
    )

    no_show_appointment = AppointmentService.mark_no_show(
        appointment_context.staff,
        appointment.id,
    )

    assert no_show_appointment.status == Appointment.STATUS_NO_SHOW


def test_mark_no_show_requires_confirmed_appointment(appointment_context):
    appointment = create_pending_appointment(appointment_context)

    with pytest.raises(BusinessException):
        AppointmentService.mark_no_show(appointment_context.staff, appointment.id)


def test_mark_no_show_rejects_other_clinic_staff(appointment_context):
    appointment = create_pending_appointment(
        appointment_context,
        status=Appointment.STATUS_CONFIRMED,
    )

    with pytest.raises(PermissionDeniedException):
        AppointmentService.mark_no_show(appointment_context.other_staff, appointment.id)
