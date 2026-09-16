import pytest

from src.models import Payment
from src.serializers.payment_serializer import PaymentCreateSerializer, PaymentSerializer
from src.tests.factories import PaymentFactory


pytestmark = pytest.mark.django_db


def test_payment_create_serializer_accepts_valid_payload():
    serializer = PaymentCreateSerializer(
        data={
            "appointment_id": 1,
            "method": Payment.METHOD_VNPAY,
            "note": "Pay online",
        },
    )

    assert serializer.is_valid(), serializer.errors


def test_payment_serializer_outputs_related_names():
    payment = PaymentFactory()

    data = PaymentSerializer(payment).data

    assert data["id"] == payment.id
    assert data["appointment_id"] == payment.appointment_id
    assert data["appointment_time"] is not None
    assert data["pet_name"] == payment.appointment.pet.name
    assert data["service_name"] == payment.appointment.service.name
    assert data["owner_name"] == payment.owner.full_name
    assert data["clinic_name"] == payment.clinic.name
