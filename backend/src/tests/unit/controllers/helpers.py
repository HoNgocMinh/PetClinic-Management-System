from datetime import timedelta
from types import SimpleNamespace

from django.utils import timezone
from rest_framework import status

from src.models import Pet, Service
from src.tests.factories import UserFactory


def make_request(user=None, data=None, query_params=None):
    return SimpleNamespace(
        user=user or UserFactory(),
        data=data or {},
        query_params=query_params or {},
    )


def assert_success(response, status_code=status.HTTP_200_OK):
    assert response.status_code == status_code
    assert response.data["success"] is True
    return response.data["data"]


def appointment_payload(appointment):
    return {
        "pet_id": appointment.pet_id,
        "clinic_id": appointment.clinic_id,
        "service_id": appointment.service_id,
        "appointment_time": timezone.now() + timedelta(days=2),
        "note": "Need a checkup",
    }


def service_payload(clinic):
    return {
        "clinic_id": clinic.id,
        "name": "General exam",
        "service_type": Service.SERVICE_EXAM,
        "description": "",
        "price": "100000.00",
        "duration_minutes": 60,
    }


def pet_payload():
    return {
        "name": "Milu",
        "species": Pet.SPECIES_DOG,
        "breed": "",
        "gender": Pet.GENDER_MALE,
        "weight": "4.50",
        "note": "",
    }


def medicine_payload():
    return {
        "name": "Vitamin",
        "unit": "tablet",
        "description": "",
        "stock_quantity": 10,
        "price": "5000.00",
    }


def medical_record_payload():
    return {
        "symptoms": "Cough",
        "diagnosis": "Cold",
        "treatment": "",
        "note": "",
    }


def prescription_item_payload(medicine):
    return {
        "medicine_id": medicine.id,
        "quantity": 1,
        "dosage": "1 tablet",
        "frequency": "twice daily",
        "duration_days": 5,
        "instruction": "",
    }
