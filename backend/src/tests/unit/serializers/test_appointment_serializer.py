from datetime import timedelta

import pytest
from django.utils import timezone

from src.serializers.appointment_serializer import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AppointmentUpdateSerializer,
)
from src.tests.factories import AppointmentFactory, MedicalRecordFactory
from src.tests.unit.serializers.helpers import assert_validation_error


pytestmark = pytest.mark.django_db


def test_appointment_serializers_validate_future_appointment_time():
    future_time = timezone.now() + timedelta(days=1)
    past_time = timezone.now() - timedelta(minutes=1)

    create_serializer = AppointmentCreateSerializer()
    update_serializer = AppointmentUpdateSerializer()

    assert create_serializer.validate_appointment_time(future_time) == future_time
    assert update_serializer.validate_appointment_time(future_time) == future_time
    assert_validation_error(create_serializer.validate_appointment_time, past_time)
    assert_validation_error(update_serializer.validate_appointment_time, past_time)

    payload = {
        "pet_id": 1,
        "clinic_id": 2,
        "service_id": 3,
        "appointment_time": future_time,
        "note": "",
    }
    serializer = AppointmentCreateSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors


def test_appointment_serializer_outputs_medical_record_id():
    appointment_without_record = AppointmentFactory()
    data_without_record = AppointmentSerializer(appointment_without_record).data
    assert data_without_record["medical_record_id"] is None

    record = MedicalRecordFactory()
    data_with_record = AppointmentSerializer(record.appointment).data
    assert data_with_record["medical_record_id"] == record.id
