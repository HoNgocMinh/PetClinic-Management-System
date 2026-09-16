from types import SimpleNamespace

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Appointment, Payment
from src.tests.factories import AppointmentFactory, PaymentFactory, UserFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_context():
    owner = UserFactory()
    other_owner = UserFactory()
    appointment = AppointmentFactory(
        owner=owner,
        status=Appointment.STATUS_WAITING_PAYMENT,
    )
    return SimpleNamespace(
        client=APIClient(),
        owner=owner,
        other_owner=other_owner,
        appointment=appointment,
    )


def authenticate(ctx, user):
    ctx.client.force_authenticate(user=user)


def test_pet_owner_can_create_view_list_and_start_vnpay_payment(payment_context, settings):
    authenticate(payment_context, payment_context.owner)
    settings.VNPAY_TMN_CODE = "TESTCODE"
    settings.VNPAY_HASH_SECRET = "TESTSECRET"
    settings.VNPAY_PAYMENT_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    settings.VNPAY_RETURN_URL = "http://localhost:5173/payment-result"

    create_response = payment_context.client.post(
        reverse("payment-list-create"),
        {
            "appointment_id": payment_context.appointment.id,
            "method": Payment.METHOD_VNPAY,
        },
        format="json",
    )

    payment_id = create_response.data["data"]["id"]
    list_response = payment_context.client.get(reverse("payment-list-create"))
    detail_response = payment_context.client.get(
        reverse("payment-detail", kwargs={"payment_id": payment_id}),
    )
    create_url_response = payment_context.client.post(
        reverse("payment-vnpay-create-url", kwargs={"payment_id": payment_id}),
        format="json",
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    assert create_response.data["data"]["amount"] == "100000.00"
    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["data"]) == 1
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data["data"]["id"] == payment_id
    assert create_url_response.status_code == status.HTTP_200_OK
    assert create_url_response.data["data"]["payment_url"].startswith(settings.VNPAY_PAYMENT_URL)
    payment_context.appointment.refresh_from_db()
    assert payment_context.appointment.status == Appointment.STATUS_WAITING_PAYMENT


def test_pet_owner_cannot_pay_another_owners_appointment(payment_context):
    authenticate(payment_context, payment_context.other_owner)

    response = payment_context.client.post(
        reverse("payment-list-create"),
        {
            "appointment_id": payment_context.appointment.id,
            "method": Payment.METHOD_VNPAY,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False


def test_pet_owner_can_only_view_their_own_payments(payment_context):
    owner_payment = PaymentFactory(owner=payment_context.owner)
    PaymentFactory(owner=payment_context.other_owner)
    authenticate(payment_context, payment_context.owner)

    response = payment_context.client.get(reverse("payment-list-create"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]) == 1
    assert response.data["data"][0]["id"] == owner_payment.id
