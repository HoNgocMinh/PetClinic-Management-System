from src.models import Appointment, Payment


class PaymentRepository:
    @staticmethod
    def create(**kwargs):
        return Payment.objects.create(**kwargs)

    @staticmethod
    def get_all_by_owner(owner):
        return Payment.objects.select_related(
            "appointment",
            "appointment__pet",
            "appointment__service",
            "owner",
            "clinic",
        ).filter(owner=owner).order_by("-created_at")

    @staticmethod
    def get_by_id(payment_id: int):
        return Payment.objects.select_related(
            "appointment",
            "appointment__pet",
            "appointment__service",
            "owner",
            "clinic",
        ).filter(id=payment_id).first()

    @staticmethod
    def get_by_id_for_update(payment_id: int):
        return Payment.objects.select_related(
            "appointment",
            "appointment__pet",
            "appointment__service",
            "owner",
            "clinic",
        ).select_for_update().filter(id=payment_id).first()

    @staticmethod
    def get_by_appointment_id(appointment_id: int):
        return Payment.objects.filter(appointment_id=appointment_id).first()

    @staticmethod
    def get_appointment_for_payment(appointment_id: int):
        return Appointment.objects.select_related(
            "owner",
            "pet",
            "clinic",
            "service",
            "medical_record",
            "medical_record__prescription",
        ).prefetch_related(
            "medical_record__prescription__items__medicine",
        ).filter(id=appointment_id).first()

    @staticmethod
    def save(payment: Payment):
        payment.save()
        return payment
