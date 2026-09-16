from types import SimpleNamespace

import pytest

from src.common.exceptions import BusinessException, NotFoundException
from src.services.clinic_service import ClinicService, ServiceService
from src.tests.factories import ClinicFactory, ServiceFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def clinic_context():
    return SimpleNamespace(
        clinic=ClinicFactory(),
        other_clinic=ClinicFactory(),
    )


@pytest.fixture
def service_context():
    return SimpleNamespace(
        clinic=ClinicFactory(),
        other_clinic=ClinicFactory(),
        inactive_clinic=ClinicFactory(is_active=False),
    )


def clinic_data(**overrides):
    data = {
        "name": "Clinic A",
        "address": "123 Main St",
        "phone": "12345",
        "email": "clinic@example.com",
    }
    data.update(overrides)
    return data


def service_data(clinic, **overrides):
    data = {
        "name": "Service A",
        "service_type": "Type",
        "price": 100,
        "duration_minutes": 60,
        "clinic_id": clinic.id,
    }
    data.update(overrides)
    return data


def test_create_clinic_success():
    clinic = ClinicService.create_clinic(clinic_data())

    assert clinic.name == "Clinic A"
    assert clinic.address == "123 Main St"
    assert clinic.phone == "12345"
    assert clinic.email == "clinic@example.com"
    assert clinic.is_active is True


def test_create_clinic_missing_optional_fields():
    clinic = ClinicService.create_clinic(clinic_data(phone="", email=""))

    assert clinic.phone == ""
    assert clinic.email == ""


def test_get_all_clinics_filters_inactive(clinic_context):
    inactive_clinic = ClinicFactory(is_active=False)

    clinics = ClinicService.get_all_clinics()

    assert clinic_context.clinic in clinics
    assert inactive_clinic not in clinics


def test_get_clinic_detail_success(clinic_context):
    result = ClinicService.get_clinic_detail(clinic_context.clinic.id)

    assert result == clinic_context.clinic


def test_get_clinic_detail_not_found():
    with pytest.raises(NotFoundException):
        ClinicService.get_clinic_detail(999999)


def test_get_clinic_detail_inactive():
    inactive_clinic = ClinicFactory(is_active=False)

    with pytest.raises(BusinessException):
        ClinicService.get_clinic_detail(inactive_clinic.id)


def test_update_clinic_success(clinic_context):
    data = {
        "name": "Updated Clinic",
        "phone": "54321",
        "email": "updated@example.com",
        "address": "456 St",
    }

    updated = ClinicService.update_clinic(clinic_context.clinic.id, data)

    assert updated.name == "Updated Clinic"
    assert updated.phone == "54321"
    assert updated.email == "updated@example.com"
    assert updated.address == "456 St"


def test_update_clinic_not_found():
    with pytest.raises(NotFoundException):
        ClinicService.update_clinic(999999, {})


def test_delete_clinic_soft_delete(clinic_context):
    ClinicService.delete_clinic(clinic_context.clinic.id)

    clinic_context.clinic.refresh_from_db()
    assert clinic_context.clinic.is_active is False


def test_delete_clinic_not_found():
    with pytest.raises(NotFoundException):
        ClinicService.delete_clinic(999999)


def test_create_service_success(service_context):
    service = ServiceService.create_service(service_data(service_context.clinic))

    assert service.name == "Service A"
    assert service.clinic == service_context.clinic


def test_create_service_missing_clinic(service_context):
    with pytest.raises(NotFoundException):
        ServiceService.create_service(service_data(service_context.clinic, clinic_id=999999))


def test_create_service_inactive_clinic(service_context):
    with pytest.raises(BusinessException):
        ServiceService.create_service(
            service_data(service_context.clinic, clinic_id=service_context.inactive_clinic.id),
        )


def test_update_service_success(service_context):
    service = ServiceFactory(clinic=service_context.clinic)

    updated = ServiceService.update_service(service.id, {"name": "Updated"})

    assert updated.name == "Updated"


def test_update_service_not_found():
    with pytest.raises(NotFoundException):
        ServiceService.update_service(999999, {})


def test_update_service_inactive_clinic(service_context):
    service = ServiceFactory(clinic=service_context.inactive_clinic)

    with pytest.raises(BusinessException):
        ServiceService.update_service(service.id, {})


def test_delete_service_success(service_context):
    service = ServiceFactory(clinic=service_context.clinic)

    ServiceService.delete_service(service.id)

    service.refresh_from_db()
    assert service.is_active is False


def test_delete_service_not_found():
    with pytest.raises(NotFoundException):
        ServiceService.delete_service(999999)
