from decimal import Decimal
import hashlib
import hmac
from datetime import timedelta
from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)
from src.models import Appointment, Payment
from src.repositories.payment_repository import PaymentRepository


class PaymentService:
    VNPAY_SUCCESS_RESPONSE_CODE = "00"

    @staticmethod
    def _validate_owner_payment(user, payment):
        if not payment:
            raise NotFoundException("Khong tim thay thanh toan.")

        if payment.owner_id != user.id:
            raise PermissionDeniedException("Ban khong co quyen truy cap thanh toan nay.")

        return payment

    @staticmethod
    def _get_owner_payment(user, payment_id):
        payment = PaymentRepository.get_by_id(payment_id)
        return PaymentService._validate_owner_payment(user, payment)

    @staticmethod
    def _calculate_amount(appointment):
        amount = appointment.service.price

        medical_record = getattr(appointment, "medical_record", None)
        if not medical_record:
            return amount

        prescription = getattr(medical_record, "prescription", None)
        if not prescription:
            return amount

        for item in prescription.items.all():
            amount += item.medicine.price * Decimal(item.quantity)

        return amount

    @staticmethod
    def _vnpay_signed_query(params):
        sorted_params = sorted(
            (key, value)
            for key, value in params.items()
            if value is not None and value != ""
        )
        sign_data = "&".join(
            f"{quote_plus(str(key))}={quote_plus(str(value))}"
            for key, value in sorted_params
        )
        secure_hash = hmac.new(
            settings.VNPAY_HASH_SECRET.encode("utf-8"),
            sign_data.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()
        return f"{urlencode(sorted_params)}&vnp_SecureHash={secure_hash}"

    @staticmethod
    def _verify_vnpay_signature(params):
        received_hash = params.get("vnp_SecureHash")
        if not received_hash:
            return False

        signed_params = {
            key: value
            for key, value in params.items()
            if key not in ["vnp_SecureHash", "vnp_SecureHashType"]
        }
        expected_query = PaymentService._vnpay_signed_query(signed_params)
        expected_hash = expected_query.rsplit("vnp_SecureHash=", 1)[1]
        return hmac.compare_digest(received_hash.lower(), expected_hash.lower())

    @staticmethod
    def _get_client_ip(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "127.0.0.1")

    @staticmethod
    def get_user_payments(user):
        return PaymentRepository.get_all_by_owner(user)

    @staticmethod
    def get_payment_detail(user, payment_id):
        return PaymentService._get_owner_payment(user, payment_id)

    @staticmethod
    def create_payment(user, data):
        appointment = PaymentRepository.get_appointment_for_payment(data["appointment_id"])
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if appointment.owner_id != user.id:
            raise PermissionDeniedException("Ban khong co quyen thanh toan lich hen nay.")

        if appointment.status != Appointment.STATUS_WAITING_PAYMENT:
            raise BusinessException("Chi co the thanh toan lich hen dang cho thanh toan.")

        existing_payment = PaymentRepository.get_by_appointment_id(appointment.id)
        if existing_payment:
            raise BusinessException("Lich hen nay da co thanh toan.")

        return PaymentRepository.create(
            appointment=appointment,
            owner=appointment.owner,
            clinic=appointment.clinic,
            amount=PaymentService._calculate_amount(appointment),
            method=data.get("method", Payment.METHOD_VNPAY),
            status=Payment.STATUS_PENDING,
            note=data.get("note", ""),
        )

    @staticmethod
    def create_pending_payment_for_appointment(appointment):
        if appointment.status != Appointment.STATUS_WAITING_PAYMENT:
            raise BusinessException("Chi co the tao thanh toan cho lich hen dang cho thanh toan.")

        existing_payment = PaymentRepository.get_by_appointment_id(appointment.id)
        if existing_payment:
            return existing_payment

        return PaymentRepository.create(
            appointment=appointment,
            owner=appointment.owner,
            clinic=appointment.clinic,
            amount=PaymentService._calculate_amount(appointment),
            method=Payment.METHOD_VNPAY,
            status=Payment.STATUS_PENDING,
        )

    @staticmethod
    def create_vnpay_payment_url(user, payment_id, request):
        payment = PaymentService._get_owner_payment(user, payment_id)

        if payment.status == Payment.STATUS_PAID:
            raise BusinessException("Thanh toan nay da hoan tat.")

        if payment.status != Payment.STATUS_PENDING:
            raise BusinessException("Chi co the thanh toan giao dich dang cho xu ly.")

        if not settings.VNPAY_TMN_CODE or not settings.VNPAY_HASH_SECRET:
            raise BusinessException("Chua cau hinh VNPAY.")

        if payment.method != Payment.METHOD_VNPAY:
            payment.method = Payment.METHOD_VNPAY
            PaymentRepository.save(payment)

        now = timezone.localtime()
        expire_at = now + timedelta(minutes=15)
        params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": settings.VNPAY_TMN_CODE,
            "vnp_Amount": int(payment.amount * Decimal("100")),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": str(payment.id),
            "vnp_OrderInfo": f"Thanh toan lich hen {payment.appointment_id}",
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": settings.VNPAY_RETURN_URL,
            "vnp_IpAddr": PaymentService._get_client_ip(request),
            "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
            "vnp_ExpireDate": expire_at.strftime("%Y%m%d%H%M%S"),
        }

        return f"{settings.VNPAY_PAYMENT_URL}?{PaymentService._vnpay_signed_query(params)}"

    @staticmethod
    def handle_vnpay_ipn(params):
        if not PaymentService._verify_vnpay_signature(params):
            return {"RspCode": "97", "Message": "Invalid signature"}

        payment_id = params.get("vnp_TxnRef")
        if not payment_id:
            return {"RspCode": "01", "Message": "Order not found"}

        with transaction.atomic():
            payment = PaymentRepository.get_by_id_for_update(payment_id)
            if not payment:
                return {"RspCode": "01", "Message": "Order not found"}

            expected_amount = int(payment.amount * Decimal("100"))
            if str(expected_amount) != str(params.get("vnp_Amount")):
                return {"RspCode": "04", "Message": "Invalid amount"}

            if payment.status != Payment.STATUS_PENDING:
                return {"RspCode": "02", "Message": "Order already confirmed"}

            payment.method = Payment.METHOD_VNPAY
            payment.transaction_code = (
                params.get("vnp_TransactionNo")
                or params.get("vnp_BankTranNo")
                or f"VNPAY-{payment.id}"
            )

            if params.get("vnp_ResponseCode") == PaymentService.VNPAY_SUCCESS_RESPONSE_CODE:
                payment.status = Payment.STATUS_PAID
                payment.paid_at = timezone.now()
                payment.appointment.status = Appointment.STATUS_COMPLETED
                payment.appointment.save()
            else:
                payment.status = Payment.STATUS_FAILED

            PaymentRepository.save(payment)

        return {"RspCode": "00", "Message": "Confirm Success"}

    @staticmethod
    def handle_vnpay_return(params):
        if not PaymentService._verify_vnpay_signature(params):
            raise BusinessException("Chu ky VNPAY khong hop le.")

        payment_id = params.get("vnp_TxnRef")
        if not payment_id:
            raise NotFoundException("Khong tim thay thanh toan.")

        with transaction.atomic():
            payment = PaymentRepository.get_by_id_for_update(payment_id)
            if not payment:
                raise NotFoundException("Khong tim thay thanh toan.")

            expected_amount = int(payment.amount * Decimal("100"))
            if str(expected_amount) != str(params.get("vnp_Amount")):
                raise BusinessException("So tien thanh toan khong hop le.")

            is_success = params.get("vnp_ResponseCode") == PaymentService.VNPAY_SUCCESS_RESPONSE_CODE

            if is_success and payment.status == Payment.STATUS_PENDING:
                payment.method = Payment.METHOD_VNPAY
                payment.status = Payment.STATUS_PAID
                payment.paid_at = timezone.now()
                payment.transaction_code = (
                    params.get("vnp_TransactionNo")
                    or params.get("vnp_BankTranNo")
                    or f"VNPAY-{payment.id}"
                )
                payment.appointment.status = Appointment.STATUS_COMPLETED
                payment.appointment.save()
                PaymentRepository.save(payment)

            return {
                "payment_id": payment.id,
                "appointment_id": payment.appointment_id,
                "payment_status": payment.status,
                "appointment_status": payment.appointment.status,
                "is_success": is_success and payment.status == Payment.STATUS_PAID,
                "response_code": params.get("vnp_ResponseCode"),
            }
