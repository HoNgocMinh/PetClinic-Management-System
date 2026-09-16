from django.conf import settings
from django.db import models

from src.common.base_model import TimeStampedModel


class Payment(TimeStampedModel):
    METHOD_CASH = "CASH"
    METHOD_VNPAY = "VNPAY"

    METHOD_CHOICES = [
        (METHOD_CASH, "Cash"),
        (METHOD_VNPAY, "VNPAY"),
    ]

    STATUS_PENDING = "PENDING"
    STATUS_PAID = "PAID"
    STATUS_FAILED = "FAILED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    appointment = models.OneToOneField(
        "src.Appointment",
        on_delete=models.PROTECT,
        related_name="payment",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    clinic = models.ForeignKey(
        "src.Clinic",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default=METHOD_VNPAY,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    transaction_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]
        verbose_name = "Thanh toán"
        verbose_name_plural = "Thanh toán"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name="payment_amount_non_negative",
            ),
        ]

    def __str__(self):
        return f"Payment #{self.id} - Appointment #{self.appointment_id}"
