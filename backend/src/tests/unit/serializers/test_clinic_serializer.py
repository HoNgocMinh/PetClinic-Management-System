import pytest

from src.models import Service
from src.serializers.clinic_serializer import (
    ClinicCreateSerializer,
    ClinicUpdateSerializer,
    ServiceCreateSerializer,
    ServiceUpdateSerializer,
)
from src.tests.unit.serializers.helpers import assert_validation_error


pytestmark = pytest.mark.django_db


def test_clinic_and_service_serializers_validate_required_business_fields():
    clinic_create = ClinicCreateSerializer()
    clinic_update = ClinicUpdateSerializer()
    service_create = ServiceCreateSerializer()
    service_update = ServiceUpdateSerializer()

    assert clinic_create.validate_name(" Clinic ") == "Clinic"
    assert clinic_create.validate_address(" 123 Street ") == "123 Street"
    assert clinic_update.validate_name(" Updated ") == "Updated"
    assert clinic_update.validate_address(" 456 Street ") == "456 Street"
    assert service_create.validate_name(" Exam ") == "Exam"
    assert service_create.validate_price(10) == 10
    assert service_create.validate_duration_minutes(30) == 30
    assert service_update.validate_name(" Grooming ") == "Grooming"
    assert service_update.validate_price(20) == 20
    assert service_update.validate_duration_minutes(45) == 45

    for callable_ in [
        clinic_create.validate_name,
        clinic_create.validate_address,
        clinic_update.validate_name,
        clinic_update.validate_address,
        service_create.validate_name,
        service_update.validate_name,
    ]:
        assert_validation_error(callable_, "   ")

    for callable_ in [service_create.validate_price, service_update.validate_price]:
        assert_validation_error(callable_, 0)

    for callable_ in [
        service_create.validate_duration_minutes,
        service_update.validate_duration_minutes,
    ]:
        assert_validation_error(callable_, 0)

    service_payload = {
        "clinic_id": 1,
        "name": "Exam",
        "service_type": Service.SERVICE_EXAM,
        "description": "",
        "price": "100000.00",
        "duration_minutes": 60,
    }
    serializer = ServiceCreateSerializer(data=service_payload)
    assert serializer.is_valid(), serializer.errors
