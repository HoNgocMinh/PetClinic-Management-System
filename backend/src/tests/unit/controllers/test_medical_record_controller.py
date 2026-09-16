import pytest
from rest_framework import status

from src.controllers.medical_record_controller import (
    AppointmentMedicalRecordAPIView,
    MedicalRecordDetailAPIView,
    PetMedicalRecordListAPIView,
    PetOwnerMedicalRecordDetailAPIView,
    PetOwnerMedicalRecordListAPIView,
)
from src.tests.factories import (
    AppointmentFactory,
    ClinicFactory,
    MedicalRecordFactory,
    PetFactory,
    ServiceFactory,
    StaffUserFactory,
    UserFactory,
)
from src.tests.unit.controllers.helpers import (
    assert_success,
    make_request,
    medical_record_payload,
)


pytestmark = pytest.mark.django_db


def test_medical_record_controller_delegates_staff_and_owner_flows(mocker):
    clinic = ClinicFactory()
    owner = UserFactory()
    staff = StaffUserFactory(clinic=clinic)
    pet = PetFactory(owner=owner)
    service = ServiceFactory(clinic=clinic)
    appointment = AppointmentFactory(owner=owner, pet=pet, clinic=clinic, service=service)
    record = MedicalRecordFactory(appointment=appointment, pet=pet, clinic=clinic, staff=staff)

    mocker.patch(
        "src.controllers.medical_record_controller.MedicalRecordService.get_medical_record_by_appointment",
        return_value=record,
    )
    assert_success(AppointmentMedicalRecordAPIView().get(make_request(staff), appointment.id))

    mocker.patch(
        "src.controllers.medical_record_controller.MedicalRecordService.create_medical_record",
        return_value=record,
    )
    assert_success(
        AppointmentMedicalRecordAPIView().post(
            make_request(staff, medical_record_payload()),
            appointment.id,
        ),
        status.HTTP_201_CREATED,
    )

    mocker.patch(
        "src.controllers.medical_record_controller.MedicalRecordService.get_medical_record_detail",
        return_value=record,
    )
    assert_success(MedicalRecordDetailAPIView().get(make_request(staff), record.id))

    mocker.patch(
        "src.controllers.medical_record_controller.MedicalRecordService.update_medical_record",
        return_value=record,
    )
    assert_success(
        MedicalRecordDetailAPIView().put(make_request(staff, {"symptoms": "Cough"}), record.id),
    )

    mocker.patch(
        "src.controllers.medical_record_controller.MedicalRecordService.get_pet_medical_records",
        return_value=[record],
    )
    assert_success(PetMedicalRecordListAPIView().get(make_request(staff), pet.id))

    mocker.patch(
        "src.controllers.medical_record_controller.MedicalRecordService.get_pet_owner_medical_records",
        return_value=[record],
    )
    assert_success(PetOwnerMedicalRecordListAPIView().get(make_request(owner), pet.id))

    mocker.patch(
        "src.controllers.medical_record_controller.MedicalRecordService.get_pet_owner_medical_record_detail",
        return_value=record,
    )
    assert_success(PetOwnerMedicalRecordDetailAPIView().get(make_request(owner), record.id))
