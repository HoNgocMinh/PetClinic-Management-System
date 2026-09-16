from types import SimpleNamespace

import pytest

from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)
from src.models import Appointment, Pet, PrescriptionItem
from src.services.prescription_service import PrescriptionService
from src.tests.factories import (
    AppointmentFactory,
    ClinicFactory,
    MedicalRecordFactory,
    MedicineFactory,
    PetFactory,
    PrescriptionFactory,
    ServiceFactory,
    StaffUserFactory,
    UserFactory,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def prescription_context():
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
    second_pet = PetFactory(
        owner=owner,
        name="Luna",
        species=Pet.SPECIES_CAT,
        gender=Pet.GENDER_FEMALE,
    )
    other_pet = PetFactory(
        owner=other_owner,
        name="Mina",
        species=Pet.SPECIES_CAT,
        gender=Pet.GENDER_FEMALE,
    )

    appointment = AppointmentFactory(
        owner=owner,
        pet=pet,
        clinic=clinic,
        service=service,
        status=Appointment.STATUS_COMPLETED,
    )
    medical_record = MedicalRecordFactory(
        appointment=appointment,
        pet=pet,
        clinic=clinic,
        staff=staff,
        symptoms="Coughing",
        diagnosis="Mild respiratory infection",
    )
    empty_appointment = AppointmentFactory(
        owner=owner,
        pet=second_pet,
        clinic=clinic,
        service=service,
        status=Appointment.STATUS_COMPLETED,
    )
    empty_medical_record = MedicalRecordFactory(
        appointment=empty_appointment,
        pet=second_pet,
        clinic=clinic,
        staff=staff,
        symptoms="Sneezing",
        diagnosis="Mild allergy",
    )
    other_appointment = AppointmentFactory(
        owner=other_owner,
        pet=other_pet,
        clinic=other_clinic,
        service=other_service,
        status=Appointment.STATUS_COMPLETED,
    )
    other_medical_record = MedicalRecordFactory(
        appointment=other_appointment,
        pet=other_pet,
        clinic=other_clinic,
        staff=other_staff,
        symptoms="Fever",
        diagnosis="Viral infection",
    )
    prescription = PrescriptionFactory(
        medical_record=medical_record,
        clinic=clinic,
        staff=staff,
        note="",
    )
    other_prescription = PrescriptionFactory(
        medical_record=other_medical_record,
        clinic=other_clinic,
        staff=other_staff,
        note="",
    )
    medicine = MedicineFactory(
        clinic=clinic,
        name="Amoxicillin",
        unit="tablet",
        stock_quantity=10,
        price=5000,
    )
    other_medicine = MedicineFactory(
        clinic=other_clinic,
        name="Cephalexin",
        unit="capsule",
        stock_quantity=10,
        price=6000,
    )

    return SimpleNamespace(
        owner=owner,
        clinic=clinic,
        staff=staff,
        other_owner=other_owner,
        other_clinic=other_clinic,
        other_staff=other_staff,
        service=service,
        other_service=other_service,
        pet=pet,
        second_pet=second_pet,
        other_pet=other_pet,
        appointment=appointment,
        medical_record=medical_record,
        empty_appointment=empty_appointment,
        empty_medical_record=empty_medical_record,
        other_appointment=other_appointment,
        other_medical_record=other_medical_record,
        prescription=prescription,
        other_prescription=other_prescription,
        medicine=medicine,
        other_medicine=other_medicine,
    )


def prescription_item_data(ctx, quantity=4):
    return {
        "medicine_id": ctx.medicine.id,
        "quantity": quantity,
        "dosage": "1 tablet",
        "frequency": "Twice daily",
        "duration_days": 5,
        "instruction": "After meal",
    }


def add_prescription_item(ctx, quantity=4):
    return PrescriptionService.add_prescription_item(
        ctx.staff,
        ctx.prescription.id,
        prescription_item_data(ctx, quantity=quantity),
    )


def test_create_prescription_success(prescription_context):
    prescription = PrescriptionService.create_prescription(
        prescription_context.staff,
        prescription_context.empty_medical_record.id,
        {"note": "Take medicine after meals"},
    )

    assert prescription.medical_record == prescription_context.empty_medical_record
    assert prescription.clinic == prescription_context.clinic
    assert prescription.staff == prescription_context.staff
    assert prescription.note == "Take medicine after meals"


def test_create_prescription_rejects_duplicate_for_medical_record(prescription_context):
    with pytest.raises(BusinessException):
        PrescriptionService.create_prescription(
            prescription_context.staff,
            prescription_context.medical_record.id,
            {"note": "Duplicate"},
        )


def test_create_prescription_rejects_missing_medical_record(prescription_context):
    with pytest.raises(NotFoundException):
        PrescriptionService.create_prescription(
            prescription_context.staff,
            999999,
            {"note": "Missing record"},
        )


def test_create_prescription_rejects_other_clinic_medical_record(prescription_context):
    with pytest.raises(PermissionDeniedException):
        PrescriptionService.create_prescription(
            prescription_context.staff,
            prescription_context.other_medical_record.id,
            {"note": "Wrong clinic"},
        )


def test_get_prescription_by_medical_record_success(prescription_context):
    prescription = PrescriptionService.get_prescription_by_medical_record(
        prescription_context.staff,
        prescription_context.medical_record.id,
    )

    assert prescription == prescription_context.prescription


def test_get_prescription_by_medical_record_rejects_missing_prescription(
    prescription_context,
):
    with pytest.raises(NotFoundException):
        PrescriptionService.get_prescription_by_medical_record(
            prescription_context.staff,
            prescription_context.empty_medical_record.id,
        )


def test_pet_owner_can_get_prescription_by_medical_record(prescription_context):
    prescription = PrescriptionService.get_pet_owner_prescription_by_medical_record(
        prescription_context.owner,
        prescription_context.medical_record.id,
    )

    assert prescription == prescription_context.prescription


def test_pet_owner_prescription_rejects_another_owner_record(prescription_context):
    with pytest.raises(PermissionDeniedException):
        PrescriptionService.get_pet_owner_prescription_by_medical_record(
            prescription_context.other_owner,
            prescription_context.medical_record.id,
        )


def test_pet_owner_prescription_rejects_missing_record(prescription_context):
    with pytest.raises(NotFoundException):
        PrescriptionService.get_pet_owner_prescription_by_medical_record(
            prescription_context.owner,
            999999,
        )


def test_pet_owner_prescription_rejects_missing_prescription(prescription_context):
    with pytest.raises(NotFoundException):
        PrescriptionService.get_pet_owner_prescription_by_medical_record(
            prescription_context.owner,
            prescription_context.empty_medical_record.id,
        )


def test_get_prescription_detail_success(prescription_context):
    prescription = PrescriptionService.get_prescription_detail(
        prescription_context.staff,
        prescription_context.prescription.id,
    )

    assert prescription == prescription_context.prescription


def test_get_prescription_detail_rejects_missing_prescription(prescription_context):
    with pytest.raises(NotFoundException):
        PrescriptionService.get_prescription_detail(prescription_context.staff, 999999)


def test_get_prescription_detail_rejects_other_clinic_prescription(prescription_context):
    with pytest.raises(PermissionDeniedException):
        PrescriptionService.get_prescription_detail(
            prescription_context.staff,
            prescription_context.other_prescription.id,
        )


def test_update_prescription_success(prescription_context):
    prescription = PrescriptionService.update_prescription(
        prescription_context.staff,
        prescription_context.prescription.id,
        {"note": "Updated note"},
    )

    assert prescription.note == "Updated note"


def test_update_prescription_rejects_user_without_clinic(prescription_context):
    with pytest.raises(BusinessException):
        PrescriptionService.update_prescription(
            prescription_context.owner,
            prescription_context.prescription.id,
            {"note": "Updated note"},
        )


def test_add_prescription_item_decreases_medicine_stock(prescription_context):
    item = add_prescription_item(prescription_context, quantity=4)

    prescription_context.medicine.refresh_from_db()
    assert item.quantity == 4
    assert prescription_context.medicine.stock_quantity == 6


def test_add_prescription_item_rejects_quantity_greater_than_stock(prescription_context):
    with pytest.raises(BusinessException):
        add_prescription_item(prescription_context, quantity=11)

    prescription_context.medicine.refresh_from_db()
    assert prescription_context.medicine.stock_quantity == 10
    assert PrescriptionItem.objects.count() == 0


def test_add_prescription_item_rejects_duplicate_medicine(prescription_context):
    add_prescription_item(prescription_context, quantity=2)

    with pytest.raises(BusinessException):
        add_prescription_item(prescription_context, quantity=2)

    prescription_context.medicine.refresh_from_db()
    assert prescription_context.medicine.stock_quantity == 8
    assert PrescriptionItem.objects.count() == 1


def test_add_prescription_item_rejects_missing_medicine(prescription_context):
    with pytest.raises(NotFoundException):
        PrescriptionService.add_prescription_item(
            prescription_context.staff,
            prescription_context.prescription.id,
            {
                **prescription_item_data(prescription_context, quantity=2),
                "medicine_id": 999999,
            },
        )


def test_add_prescription_item_rejects_other_clinic_medicine(prescription_context):
    with pytest.raises(PermissionDeniedException):
        PrescriptionService.add_prescription_item(
            prescription_context.staff,
            prescription_context.prescription.id,
            {
                **prescription_item_data(prescription_context, quantity=2),
                "medicine_id": prescription_context.other_medicine.id,
            },
        )


def test_add_prescription_item_rejects_inactive_medicine(prescription_context):
    inactive_medicine = MedicineFactory(
        clinic=prescription_context.clinic,
        name="Inactive Medicine",
        unit="tablet",
        stock_quantity=10,
        price=5000,
        is_active=False,
    )

    with pytest.raises(BusinessException):
        PrescriptionService.add_prescription_item(
            prescription_context.staff,
            prescription_context.prescription.id,
            {
                **prescription_item_data(prescription_context, quantity=2),
                "medicine_id": inactive_medicine.id,
            },
        )


def test_update_prescription_item_to_higher_quantity_decreases_stock_by_diff(
    prescription_context,
):
    item = add_prescription_item(prescription_context, quantity=4)

    updated_item = PrescriptionService.update_prescription_item(
        prescription_context.staff,
        item.id,
        {"quantity": 7},
    )

    prescription_context.medicine.refresh_from_db()
    assert updated_item.quantity == 7
    assert prescription_context.medicine.stock_quantity == 3


def test_update_prescription_item_to_lower_quantity_returns_stock_by_diff(
    prescription_context,
):
    item = add_prescription_item(prescription_context, quantity=4)

    updated_item = PrescriptionService.update_prescription_item(
        prescription_context.staff,
        item.id,
        {"quantity": 2},
    )

    prescription_context.medicine.refresh_from_db()
    assert updated_item.quantity == 2
    assert prescription_context.medicine.stock_quantity == 8


def test_update_prescription_item_updates_all_editable_fields(prescription_context):
    item = add_prescription_item(prescription_context, quantity=4)

    updated_item = PrescriptionService.update_prescription_item(
        prescription_context.staff,
        item.id,
        {
            "dosage": "2 tablets",
            "frequency": "Once daily",
            "duration_days": 7,
            "instruction": "Before meal",
        },
    )

    assert updated_item.quantity == 4
    assert updated_item.dosage == "2 tablets"
    assert updated_item.frequency == "Once daily"
    assert updated_item.duration_days == 7
    assert updated_item.instruction == "Before meal"


def test_update_prescription_item_rejects_missing_item(prescription_context):
    with pytest.raises(NotFoundException):
        PrescriptionService.update_prescription_item(
            prescription_context.staff,
            999999,
            {"quantity": 2},
        )


def test_update_prescription_item_rejects_quantity_increase_greater_than_stock(
    prescription_context,
):
    item = add_prescription_item(prescription_context, quantity=4)

    with pytest.raises(BusinessException):
        PrescriptionService.update_prescription_item(
            prescription_context.staff,
            item.id,
            {"quantity": 11},
        )

    prescription_context.medicine.refresh_from_db()
    assert prescription_context.medicine.stock_quantity == 6


def test_delete_prescription_item_returns_medicine_stock(prescription_context):
    item = add_prescription_item(prescription_context, quantity=4)

    PrescriptionService.delete_prescription_item(prescription_context.staff, item.id)

    prescription_context.medicine.refresh_from_db()
    assert prescription_context.medicine.stock_quantity == 10
    assert not PrescriptionItem.objects.filter(id=item.id).exists()


def test_delete_prescription_item_rejects_missing_item(prescription_context):
    with pytest.raises(NotFoundException):
        PrescriptionService.delete_prescription_item(prescription_context.staff, 999999)
