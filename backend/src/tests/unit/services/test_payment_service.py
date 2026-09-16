from decimal import Decimal
from types import SimpleNamespace

import pytest

from src.common.exceptions import (
    BusinessException,
    PermissionDeniedException,
)
from src.models import Appointment, Payment
from src.services.payment_service import PaymentService
from src.tests.factories import (
    AppointmentFactory,
    MedicalRecordFactory,
    MedicineFactory,
    PaymentFactory,
    PrescriptionFactory,
    PrescriptionItemFactory,
    ServiceFactory,
    UserFactory,
)


pytestmark = pytest.mark.django_db


def test_create_payment_calculates_service_and_medicine_amount():
    owner = UserFactory()
    service = ServiceFactory(price=Decimal("100000.00"))
    appointment = AppointmentFactory(
        owner=owner,
        clinic=service.clinic,
        service=service,
        status=Appointment.STATUS_WAITING_PAYMENT,
    )
    record = MedicalRecordFactory(appointment=appointment)
    prescription = PrescriptionFactory(medical_record=record)
    medicine = MedicineFactory(clinic=appointment.clinic, price=Decimal("5000.00"))
    PrescriptionItemFactory(
        prescription=prescription,
        medicine=medicine,
        quantity=2,
    )

    payment = PaymentService.create_payment(
        owner,
        {
            "appointment_id": appointment.id,
            "method": Payment.METHOD_VNPAY,
        },
    )

    assert payment.owner == owner
    assert payment.clinic == appointment.clinic
    assert payment.amount == Decimal("110000.00")
    assert payment.status == Payment.STATUS_PENDING


def test_create_payment_rejects_unfinished_appointment():
    owner = UserFactory()
    appointment = AppointmentFactory(owner=owner, status=Appointment.STATUS_PENDING)

    with pytest.raises(BusinessException):
        PaymentService.create_payment(
            owner,
            {
                "appointment_id": appointment.id,
                "method": Payment.METHOD_VNPAY,
            },
        )


def test_create_payment_rejects_another_owners_appointment():
    appointment = AppointmentFactory(status=Appointment.STATUS_WAITING_PAYMENT)
    other_owner = UserFactory()

    with pytest.raises(PermissionDeniedException):
        PaymentService.create_payment(
            other_owner,
            {
                "appointment_id": appointment.id,
                "method": Payment.METHOD_VNPAY,
            },
        )


def test_create_payment_rejects_duplicate_payment():
    appointment = AppointmentFactory(status=Appointment.STATUS_WAITING_PAYMENT)
    payment = PaymentFactory(
        appointment=appointment,
        owner=appointment.owner,
        clinic=appointment.clinic,
    )

    with pytest.raises(BusinessException):
        PaymentService.create_payment(
            payment.owner,
            {
                "appointment_id": payment.appointment_id,
                "method": Payment.METHOD_VNPAY,
            },
        )


def test_create_vnpay_payment_url_returns_signed_sandbox_url(settings):
    appointment = AppointmentFactory(status=Appointment.STATUS_WAITING_PAYMENT)
    payment = PaymentFactory(
        appointment=appointment,
        owner=appointment.owner,
        clinic=appointment.clinic,
        status=Payment.STATUS_PENDING,
    )
    settings.VNPAY_TMN_CODE = "TESTCODE"
    settings.VNPAY_HASH_SECRET = "TESTSECRET"
    settings.VNPAY_PAYMENT_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    settings.VNPAY_RETURN_URL = "http://localhost:5173/payment-result"
    request = SimpleNamespace(META={"REMOTE_ADDR": "127.0.0.1"})

    payment_url = PaymentService.create_vnpay_payment_url(payment.owner, payment.id, request)

    assert payment_url.startswith(settings.VNPAY_PAYMENT_URL)
    assert f"vnp_TxnRef={payment.id}" in payment_url
    assert "vnp_SecureHash=" in payment_url


def test_handle_vnpay_ipn_marks_successful_payment_as_paid(settings):
    appointment = AppointmentFactory(status=Appointment.STATUS_WAITING_PAYMENT)
    payment = PaymentFactory(
        appointment=appointment,
        owner=appointment.owner,
        clinic=appointment.clinic,
        status=Payment.STATUS_PENDING,
    )
    settings.VNPAY_HASH_SECRET = "TESTSECRET"
    params = {
        "vnp_TxnRef": str(payment.id),
        "vnp_Amount": str(int(Decimal(payment.amount) * Decimal("100"))),
        "vnp_ResponseCode": "00",
        "vnp_TransactionNo": "14123456",
    }
    signed_query = PaymentService._vnpay_signed_query(params)
    params["vnp_SecureHash"] = signed_query.rsplit("vnp_SecureHash=", 1)[1]

    result = PaymentService.handle_vnpay_ipn(params)

    assert result["RspCode"] == "00"
    payment.refresh_from_db()
    appointment.refresh_from_db()
    assert payment.status == Payment.STATUS_PAID
    assert payment.method == Payment.METHOD_VNPAY
    assert payment.transaction_code == "14123456"
    assert appointment.status == Appointment.STATUS_COMPLETED


def test_handle_vnpay_return_marks_successful_payment_as_paid(settings):
    appointment = AppointmentFactory(status=Appointment.STATUS_WAITING_PAYMENT)
    payment = PaymentFactory(
        appointment=appointment,
        owner=appointment.owner,
        clinic=appointment.clinic,
        status=Payment.STATUS_PENDING,
    )
    settings.VNPAY_HASH_SECRET = "TESTSECRET"
    params = {
        "vnp_TxnRef": str(payment.id),
        "vnp_Amount": str(int(Decimal(payment.amount) * Decimal("100"))),
        "vnp_ResponseCode": "00",
        "vnp_TransactionNo": "14999999",
    }
    signed_query = PaymentService._vnpay_signed_query(params)
    params["vnp_SecureHash"] = signed_query.rsplit("vnp_SecureHash=", 1)[1]

    result = PaymentService.handle_vnpay_return(params)

    assert result["is_success"] is True
    payment.refresh_from_db()
    appointment.refresh_from_db()
    assert payment.status == Payment.STATUS_PAID
    assert appointment.status == Appointment.STATUS_COMPLETED
