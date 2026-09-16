from decimal import Decimal
from types import SimpleNamespace

import pytest

from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)
from src.services.medicine_service import MedicineService
from src.tests.factories import ClinicFactory, MedicineFactory, StaffUserFactory, UserFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def medicine_context():
    clinic = ClinicFactory()
    other_clinic = ClinicFactory()
    return SimpleNamespace(
        clinic=clinic,
        other_clinic=other_clinic,
        staff=StaffUserFactory(clinic=clinic),
        other_staff=StaffUserFactory(clinic=other_clinic),
    )


def medicine_data(**overrides):
    data = {
        "name": "Amoxicillin",
        "unit": "tablet",
        "description": "Antibiotic",
        "stock_quantity": 10,
        "price": Decimal("5000.00"),
    }
    data.update(overrides)
    return data


def test_get_clinic_medicines_filters_by_status(medicine_context):
    active_medicine = MedicineFactory(
        clinic=medicine_context.clinic,
        name="Active Medicine",
    )
    inactive_medicine = MedicineFactory(
        clinic=medicine_context.clinic,
        name="Inactive Medicine",
        is_active=False,
    )
    MedicineFactory(clinic=medicine_context.other_clinic, name="Other Clinic Medicine")

    active_medicines = MedicineService.get_clinic_medicines(
        medicine_context.staff,
        status="active",
    )
    inactive_medicines = MedicineService.get_clinic_medicines(
        medicine_context.staff,
        status="inactive",
    )
    all_medicines = MedicineService.get_clinic_medicines(
        medicine_context.staff,
        status="all",
    )

    assert list(active_medicines) == [active_medicine]
    assert list(inactive_medicines) == [inactive_medicine]
    assert set(all_medicines) == {active_medicine, inactive_medicine}


def test_get_clinic_medicines_rejects_invalid_status(medicine_context):
    with pytest.raises(BusinessException):
        MedicineService.get_clinic_medicines(medicine_context.staff, status="archived")


def test_staff_without_clinic_cannot_access_medicines():
    user_without_clinic = UserFactory()

    with pytest.raises(BusinessException):
        MedicineService.get_clinic_medicines(user_without_clinic)


def test_get_medicine_detail_success(medicine_context):
    medicine = MedicineFactory(clinic=medicine_context.clinic)

    result = MedicineService.get_medicine_detail(medicine_context.staff, medicine.id)

    assert result == medicine


def test_get_medicine_detail_rejects_missing_medicine(medicine_context):
    with pytest.raises(NotFoundException):
        MedicineService.get_medicine_detail(medicine_context.staff, 999999)


def test_get_medicine_detail_rejects_other_clinic_medicine(medicine_context):
    medicine = MedicineFactory(clinic=medicine_context.other_clinic)

    with pytest.raises(PermissionDeniedException):
        MedicineService.get_medicine_detail(medicine_context.staff, medicine.id)


def test_create_medicine_success(medicine_context):
    medicine = MedicineService.create_medicine(medicine_context.staff, medicine_data())

    assert medicine.clinic == medicine_context.clinic
    assert medicine.name == "Amoxicillin"
    assert medicine.unit == "tablet"
    assert medicine.stock_quantity == 10
    assert medicine.price == Decimal("5000.00")
    assert medicine.is_active is True


def test_create_medicine_rejects_active_duplicate_name(medicine_context):
    MedicineFactory(clinic=medicine_context.clinic, name="Amoxicillin")

    with pytest.raises(BusinessException):
        MedicineService.create_medicine(medicine_context.staff, medicine_data())


def test_create_medicine_reactivates_inactive_existing_record(medicine_context):
    inactive_medicine = MedicineFactory(
        clinic=medicine_context.clinic,
        name="Amoxicillin",
        unit="old unit",
        stock_quantity=0,
        price=Decimal("1000.00"),
        is_active=False,
    )

    medicine = MedicineService.create_medicine(
        medicine_context.staff,
        medicine_data(unit="capsule", stock_quantity=20, price=Decimal("7000.00")),
    )

    inactive_medicine.refresh_from_db()
    assert medicine.id == inactive_medicine.id
    assert inactive_medicine.unit == "capsule"
    assert inactive_medicine.stock_quantity == 20
    assert inactive_medicine.price == Decimal("7000.00")
    assert inactive_medicine.is_active is True


def test_update_medicine_success(medicine_context):
    medicine = MedicineFactory(clinic=medicine_context.clinic, name="Amoxicillin")

    updated_medicine = MedicineService.update_medicine(
        medicine_context.staff,
        medicine.id,
        {
            "name": "Amoxicillin Updated",
            "unit": "capsule",
            "description": "Updated",
            "stock_quantity": 12,
            "price": Decimal("6000.00"),
            "is_active": False,
        },
    )

    assert updated_medicine.name == "Amoxicillin Updated"
    assert updated_medicine.unit == "capsule"
    assert updated_medicine.description == "Updated"
    assert updated_medicine.stock_quantity == 12
    assert updated_medicine.price == Decimal("6000.00")
    assert updated_medicine.is_active is False


def test_update_medicine_rejects_active_duplicate_name(medicine_context):
    medicine = MedicineFactory(clinic=medicine_context.clinic, name="Amoxicillin")
    MedicineFactory(clinic=medicine_context.clinic, name="Cephalexin")

    with pytest.raises(BusinessException):
        MedicineService.update_medicine(
            medicine_context.staff,
            medicine.id,
            {"name": "Cephalexin"},
        )


def test_update_medicine_rejects_inactive_duplicate_name(medicine_context):
    medicine = MedicineFactory(clinic=medicine_context.clinic, name="Amoxicillin")
    MedicineFactory(clinic=medicine_context.clinic, name="Cephalexin", is_active=False)

    with pytest.raises(BusinessException):
        MedicineService.update_medicine(
            medicine_context.staff,
            medicine.id,
            {"name": "Cephalexin"},
        )


def test_update_medicine_rejects_other_clinic_medicine(medicine_context):
    medicine = MedicineFactory(clinic=medicine_context.other_clinic)

    with pytest.raises(PermissionDeniedException):
        MedicineService.update_medicine(
            medicine_context.staff,
            medicine.id,
            {"name": "Updated"},
        )


def test_delete_medicine_soft_deletes_record(medicine_context):
    medicine = MedicineFactory(clinic=medicine_context.clinic)

    deleted_medicine = MedicineService.delete_medicine(medicine_context.staff, medicine.id)

    medicine.refresh_from_db()
    assert deleted_medicine.id == medicine.id
    assert medicine.is_active is False
