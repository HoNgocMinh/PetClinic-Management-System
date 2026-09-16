import pytest
from rest_framework import status

from src.controllers.clinic_controller import (
    ClinicDetailAPIView,
    ClinicListCreateAPIView,
    ServiceByClinicAPIView,
    ServiceCreateAPIView,
    ServiceUpdateDeleteAPIView,
)
from src.tests.factories import AdminUserFactory, ClinicFactory, ServiceFactory
from src.tests.unit.controllers.helpers import assert_success, make_request, service_payload


pytestmark = pytest.mark.django_db


def test_clinic_controller_delegates_clinic_and_service_flows(mocker):
    clinic = ClinicFactory()
    service = ServiceFactory(clinic=clinic)
    admin = AdminUserFactory()

    mocker.patch(
        "src.controllers.clinic_controller.ClinicService.get_all_clinics",
        return_value=[clinic],
    )
    assert_success(ClinicListCreateAPIView().get(make_request()))

    mocker.patch(
        "src.controllers.clinic_controller.ClinicService.create_clinic",
        return_value=clinic,
    )
    clinic_create_payload = {
        "name": "Happy Paws",
        "address": "123 Street",
        "phone": "",
        "email": "",
    }
    assert_success(
        ClinicListCreateAPIView().post(make_request(admin, clinic_create_payload)),
        status.HTTP_201_CREATED,
    )

    mocker.patch(
        "src.controllers.clinic_controller.ClinicService.get_clinic_detail",
        return_value=clinic,
    )
    assert_success(ClinicDetailAPIView().get(make_request(), clinic.id))

    mocker.patch(
        "src.controllers.clinic_controller.ClinicService.update_clinic",
        return_value=clinic,
    )
    assert_success(
        ClinicDetailAPIView().put(make_request(admin, {"name": "Updated"}), clinic.id),
    )

    mocker.patch("src.controllers.clinic_controller.ClinicService.delete_clinic")
    assert_success(ClinicDetailAPIView().delete(make_request(admin), clinic.id))

    mocker.patch(
        "src.controllers.clinic_controller.ServiceService.create_service",
        return_value=service,
    )
    assert_success(
        ServiceCreateAPIView().post(make_request(admin, service_payload(clinic))),
        status.HTTP_201_CREATED,
    )

    mocker.patch(
        "src.controllers.clinic_controller.ServiceService.update_service",
        return_value=service,
    )
    assert_success(
        ServiceUpdateDeleteAPIView().put(make_request(admin, {"name": "Updated"}), service.id),
    )

    mocker.patch("src.controllers.clinic_controller.ServiceService.delete_service")
    assert_success(ServiceUpdateDeleteAPIView().delete(make_request(admin), service.id))

    mocker.patch(
        "src.controllers.clinic_controller.ServiceService.get_services_by_clinic",
        return_value=[service],
    )
    assert_success(ServiceByClinicAPIView().get(make_request(), clinic.id))
