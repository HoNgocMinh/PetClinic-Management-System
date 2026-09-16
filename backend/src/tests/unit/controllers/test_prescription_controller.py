import pytest
from rest_framework import status

from src.controllers.prescription_controller import (
    MedicalRecordPrescriptionAPIView,
    PetOwnerMedicalRecordPrescriptionAPIView,
    PrescriptionDetailAPIView,
    PrescriptionItemDetailAPIView,
    PrescriptionItemListCreateAPIView,
)
from src.tests.factories import (
    AppointmentFactory,
    ClinicFactory,
    MedicalRecordFactory,
    MedicineFactory,
    PetFactory,
    PrescriptionFactory,
    PrescriptionItemFactory,
    ServiceFactory,
    StaffUserFactory,
    UserFactory,
)
from src.tests.unit.controllers.helpers import (
    assert_success,
    make_request,
    prescription_item_payload,
)


pytestmark = pytest.mark.django_db


def test_prescription_controller_delegates_prescription_flows(mocker):
    clinic = ClinicFactory()
    owner = UserFactory()
    staff = StaffUserFactory(clinic=clinic)
    pet = PetFactory(owner=owner)
    service = ServiceFactory(clinic=clinic)
    appointment = AppointmentFactory(owner=owner, pet=pet, clinic=clinic, service=service)
    record = MedicalRecordFactory(appointment=appointment, pet=pet, clinic=clinic, staff=staff)
    prescription = PrescriptionFactory(medical_record=record, clinic=clinic, staff=staff)
    medicine = MedicineFactory(clinic=clinic)
    item = PrescriptionItemFactory(prescription=prescription, medicine=medicine)

    mocker.patch(
        "src.controllers.prescription_controller.PrescriptionService.get_prescription_by_medical_record",
        return_value=prescription,
    )
    assert_success(MedicalRecordPrescriptionAPIView().get(make_request(staff), record.id))

    mocker.patch(
        "src.controllers.prescription_controller.PrescriptionService.create_prescription",
        return_value=prescription,
    )
    assert_success(
        MedicalRecordPrescriptionAPIView().post(make_request(staff, {"note": ""}), record.id),
        status.HTTP_201_CREATED,
    )

    mocker.patch(
        "src.controllers.prescription_controller.PrescriptionService.get_prescription_detail",
        return_value=prescription,
    )
    assert_success(PrescriptionDetailAPIView().get(make_request(staff), prescription.id))

    mocker.patch(
        "src.controllers.prescription_controller.PrescriptionService.update_prescription",
        return_value=prescription,
    )
    assert_success(
        PrescriptionDetailAPIView().put(make_request(staff, {"note": "Updated"}), prescription.id),
    )

    mocker.patch(
        "src.controllers.prescription_controller.PrescriptionService.add_prescription_item",
        return_value=item,
    )
    assert_success(
        PrescriptionItemListCreateAPIView().post(
            make_request(staff, prescription_item_payload(medicine)),
            prescription.id,
        ),
        status.HTTP_201_CREATED,
    )

    mocker.patch(
        "src.controllers.prescription_controller.PrescriptionService.update_prescription_item",
        return_value=item,
    )
    assert_success(
        PrescriptionItemDetailAPIView().put(make_request(staff, {"quantity": 1}), item.id),
    )

    mocker.patch("src.controllers.prescription_controller.PrescriptionService.delete_prescription_item")
    assert_success(PrescriptionItemDetailAPIView().delete(make_request(staff), item.id))

    mocker.patch(
        "src.controllers.prescription_controller.PrescriptionService.get_pet_owner_prescription_by_medical_record",
        return_value=prescription,
    )
    assert_success(PetOwnerMedicalRecordPrescriptionAPIView().get(make_request(owner), record.id))
