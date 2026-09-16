from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.utils import timezone

from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)
from src.models import Appointment, MedicalRecord, Pet
from src.services.medical_record_service import MedicalRecordService
from src.tests.factories import (
    AppointmentFactory,
    ClinicFactory,
    MedicalRecordFactory,
    PetFactory,
    ServiceFactory,
    StaffUserFactory,
    UserFactory,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def medical_record_context():
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
        pet=pet,
        other_pet=other_pet,
    )


def medical_record_data():
    return {
        "symptoms": "Coughing",
        "diagnosis": "Mild respiratory infection",
        "treatment": "Rest and medication",
        "note": "Follow up in 7 days",
    }


def create_appointment(ctx, owner=None, pet=None, status=Appointment.STATUS_CHECKED_IN):
    return AppointmentFactory(
        owner=owner or ctx.owner,
        pet=pet or ctx.pet,
        clinic=ctx.clinic,
        service=ctx.service,
        appointment_time=timezone.now() + timedelta(days=1),
        status=status,
    )


def create_medical_record(ctx, owner=None, pet=None):
    appointment = create_appointment(ctx, owner=owner, pet=pet)
    return MedicalRecordFactory(
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
        status=Appointment.STATUS_CHECKED_IN,
    )

    record = MedicalRecordService.create_medical_record(
        medical_record_context.staff,
        appointment.id,
        medical_record_data(),
    )

    assert record.appointment == appointment
    assert record.pet == medical_record_context.pet
    assert record.clinic == medical_record_context.clinic
    assert record.staff == medical_record_context.staff
    assert record.symptoms == "Coughing"
    assert record.diagnosis == "Mild respiratory infection"


def test_create_medical_record_rejects_pending_appointment(medical_record_context):
    appointment = create_appointment(
        medical_record_context,
        status=Appointment.STATUS_PENDING,
    )

    with pytest.raises(BusinessException):
        MedicalRecordService.create_medical_record(
            medical_record_context.staff,
            appointment.id,
            medical_record_data(),
        )

    assert MedicalRecord.objects.count() == 0


def test_create_medical_record_rejects_duplicate_for_same_appointment(medical_record_context):
    appointment = create_appointment(
        medical_record_context,
        status=Appointment.STATUS_CHECKED_IN,
    )
    MedicalRecordService.create_medical_record(
        medical_record_context.staff,
        appointment.id,
        medical_record_data(),
    )

    with pytest.raises(BusinessException):
        MedicalRecordService.create_medical_record(
            medical_record_context.staff,
            appointment.id,
            medical_record_data(),
        )

    assert MedicalRecord.objects.count() == 1


def test_staff_from_other_clinic_cannot_create_medical_record(medical_record_context):
    appointment = create_appointment(
        medical_record_context,
        status=Appointment.STATUS_CHECKED_IN,
    )

    with pytest.raises(PermissionDeniedException):
        MedicalRecordService.create_medical_record(
            medical_record_context.other_staff,
            appointment.id,
            medical_record_data(),
        )

    assert MedicalRecord.objects.count() == 0


def test_create_medical_record_rejects_missing_appointment(medical_record_context):
    with pytest.raises(NotFoundException):
        MedicalRecordService.create_medical_record(
            medical_record_context.staff,
            999999,
            medical_record_data(),
        )


def test_create_medical_record_requires_staff_clinic(medical_record_context):
    appointment = create_appointment(
        medical_record_context,
        status=Appointment.STATUS_CHECKED_IN,
    )

    with pytest.raises(BusinessException):
        MedicalRecordService.create_medical_record(
            medical_record_context.owner,
            appointment.id,
            medical_record_data(),
        )


def test_owner_can_get_medical_records_for_their_pet(medical_record_context):
    record = create_medical_record(medical_record_context)

    records = MedicalRecordService.get_pet_owner_medical_records(
        medical_record_context.owner,
        medical_record_context.pet.id,
    )

    assert list(records) == [record]


def test_staff_can_get_medical_record_by_appointment(medical_record_context):
    record = create_medical_record(medical_record_context)

    result = MedicalRecordService.get_medical_record_by_appointment(
        medical_record_context.staff,
        record.appointment.id,
    )

    assert result == record


def test_get_medical_record_by_appointment_rejects_missing_record(medical_record_context):
    appointment = create_appointment(
        medical_record_context,
        status=Appointment.STATUS_CHECKED_IN,
    )

    with pytest.raises(NotFoundException):
        MedicalRecordService.get_medical_record_by_appointment(
            medical_record_context.staff,
            appointment.id,
        )


def test_staff_can_get_medical_record_detail_in_same_clinic(medical_record_context):
    record = create_medical_record(medical_record_context)

    result = MedicalRecordService.get_medical_record_detail(
        medical_record_context.staff,
        record.id,
    )

    assert result == record


def test_get_medical_record_detail_rejects_missing_record(medical_record_context):
    with pytest.raises(NotFoundException):
        MedicalRecordService.get_medical_record_detail(medical_record_context.staff, 999999)


def test_get_medical_record_detail_requires_staff_clinic(medical_record_context):
    record = create_medical_record(medical_record_context)

    with pytest.raises(BusinessException):
        MedicalRecordService.get_medical_record_detail(medical_record_context.owner, record.id)


def test_staff_can_get_pet_medical_records_in_same_clinic(medical_record_context):
    record = create_medical_record(medical_record_context)

    records = MedicalRecordService.get_pet_medical_records(
        medical_record_context.staff,
        medical_record_context.pet.id,
    )

    assert list(records) == [record]


def test_get_pet_medical_records_rejects_missing_pet(medical_record_context):
    with pytest.raises(NotFoundException):
        MedicalRecordService.get_pet_medical_records(medical_record_context.staff, 999999)


def test_get_pet_medical_records_requires_staff_clinic(medical_record_context):
    with pytest.raises(BusinessException):
        MedicalRecordService.get_pet_medical_records(
            medical_record_context.owner,
            medical_record_context.pet.id,
        )


def test_owner_cannot_get_medical_records_for_another_owner_pet(medical_record_context):
    with pytest.raises(PermissionDeniedException):
        MedicalRecordService.get_pet_owner_medical_records(
            medical_record_context.owner,
            medical_record_context.other_pet.id,
        )


def test_owner_medical_records_rejects_missing_pet(medical_record_context):
    with pytest.raises(NotFoundException):
        MedicalRecordService.get_pet_owner_medical_records(
            medical_record_context.owner,
            999999,
        )


def test_owner_cannot_get_medical_record_detail_for_another_owner_pet(medical_record_context):
    record = create_medical_record(
        medical_record_context,
        owner=medical_record_context.other_owner,
        pet=medical_record_context.other_pet,
    )

    with pytest.raises(PermissionDeniedException):
        MedicalRecordService.get_pet_owner_medical_record_detail(
            medical_record_context.owner,
            record.id,
        )


def test_owner_medical_record_detail_rejects_missing_record(medical_record_context):
    with pytest.raises(NotFoundException):
        MedicalRecordService.get_pet_owner_medical_record_detail(
            medical_record_context.owner,
            999999,
        )


def test_staff_can_update_medical_record_in_same_clinic(medical_record_context):
    record = create_medical_record(medical_record_context)

    updated_record = MedicalRecordService.update_medical_record(
        medical_record_context.staff,
        record.id,
        {
            "symptoms": "Fever",
            "diagnosis": "Viral infection",
            "treatment": "Hydration",
            "note": "Monitor temperature",
        },
    )

    assert updated_record.symptoms == "Fever"
    assert updated_record.diagnosis == "Viral infection"
    assert updated_record.treatment == "Hydration"
    assert updated_record.note == "Monitor temperature"


def test_staff_from_other_clinic_cannot_update_medical_record(medical_record_context):
    record = create_medical_record(medical_record_context)

    with pytest.raises(PermissionDeniedException):
        MedicalRecordService.update_medical_record(
            medical_record_context.other_staff,
            record.id,
            {"diagnosis": "Updated diagnosis"},
        )
