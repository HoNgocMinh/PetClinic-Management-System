import pytest
from rest_framework import status

from src.controllers.medicine_controller import MedicineDetailAPIView, MedicineListCreateAPIView
from src.tests.factories import ClinicFactory, MedicineFactory, StaffUserFactory
from src.tests.unit.controllers.helpers import assert_success, make_request, medicine_payload


pytestmark = pytest.mark.django_db


def test_medicine_controller_delegates_medicine_flows(mocker):
    clinic = ClinicFactory()
    staff = StaffUserFactory(clinic=clinic)
    medicine = MedicineFactory(clinic=clinic)

    get_medicines = mocker.patch(
        "src.controllers.medicine_controller.MedicineService.get_clinic_medicines",
        return_value=[medicine],
    )
    assert_success(
        MedicineListCreateAPIView().get(make_request(staff, query_params={"status": "all"})),
    )
    get_medicines.assert_called_once_with(staff, status="all")

    mocker.patch(
        "src.controllers.medicine_controller.MedicineService.create_medicine",
        return_value=medicine,
    )
    assert_success(
        MedicineListCreateAPIView().post(make_request(staff, medicine_payload())),
        status.HTTP_201_CREATED,
    )

    mocker.patch(
        "src.controllers.medicine_controller.MedicineService.get_medicine_detail",
        return_value=medicine,
    )
    assert_success(MedicineDetailAPIView().get(make_request(staff), medicine.id))

    mocker.patch(
        "src.controllers.medicine_controller.MedicineService.update_medicine",
        return_value=medicine,
    )
    assert_success(
        MedicineDetailAPIView().put(make_request(staff, {"name": "Vitamin"}), medicine.id),
    )

    mocker.patch(
        "src.controllers.medicine_controller.MedicineService.delete_medicine",
        return_value=medicine,
    )
    assert_success(MedicineDetailAPIView().delete(make_request(staff), medicine.id))
