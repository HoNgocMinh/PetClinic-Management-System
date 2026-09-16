import pytest

from src.serializers.appointment_serializer import AppointmentSerializer
from src.serializers.clinic_serializer import ClinicSerializer, ServiceSerializer
from src.serializers.medical_record_serializer import MedicalRecordSerializer
from src.serializers.medicine_serializer import MedicineSerializer
from src.serializers.pet_serializer import PetSerializer
from src.serializers.prescription_item_serializer import PrescriptionItemSerializer
from src.serializers.prescription_serializer import PrescriptionSerializer
from src.serializers.user_serializer import UserSerializer
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


pytestmark = pytest.mark.django_db


def test_model_serializers_render_expected_fields():
    clinic = ClinicFactory(name="Happy Paws")
    owner = UserFactory(username="owner_serialized", full_name="Nguyen Van A")
    staff = StaffUserFactory(clinic=clinic, full_name="Dr Staff")
    pet = PetFactory(owner=owner, name="Milu")
    service = ServiceFactory(clinic=clinic, name="Exam")
    appointment = AppointmentFactory(owner=owner, pet=pet, clinic=clinic, service=service)
    medicine = MedicineFactory(clinic=clinic, name="Vitamin")
    record = MedicalRecordFactory(appointment=appointment, pet=pet, clinic=clinic, staff=staff)
    prescription = PrescriptionFactory(medical_record=record, clinic=clinic, staff=staff)
    item = PrescriptionItemFactory(prescription=prescription, medicine=medicine)

    assert ClinicSerializer(clinic).data["name"] == "Happy Paws"
    assert ServiceSerializer(service).data["clinic_name"] == "Happy Paws"
    assert UserSerializer(staff).data["clinic_name"] == "Happy Paws"
    assert PetSerializer(pet).data["owner_username"] == "owner_serialized"
    assert AppointmentSerializer(appointment).data["pet_name"] == "Milu"
    assert AppointmentSerializer(appointment).data["owner_full_name"] == "Nguyen Van A"
    assert MedicineSerializer(medicine).data["clinic_name"] == "Happy Paws"
    assert MedicalRecordSerializer(record).data["staff_name"] == "Dr Staff"
    assert PrescriptionItemSerializer(item).data["medicine_name"] == "Vitamin"
    assert PrescriptionSerializer(prescription).data["items"][0]["medicine_name"] == "Vitamin"
