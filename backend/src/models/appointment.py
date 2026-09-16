from django.conf import settings
from django.db import models
from src.common.base_model import TimeStampedModel


class Appointment(TimeStampedModel):
    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CHECKED_IN = "CHECKED_IN"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_WAITING_PAYMENT = "WAITING_PAYMENT"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_NO_SHOW = "NO_SHOW"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CHECKED_IN, "Checked In"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_WAITING_PAYMENT, "Waiting Payment"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_NO_SHOW, "No Show"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    pet = models.ForeignKey(
        "src.Pet",
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    clinic = models.ForeignKey(
        "src.Clinic",
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    service = models.ForeignKey(
        "src.Service",
        on_delete=models.PROTECT,
        related_name="appointments"
    )
    appointment_time = models.DateTimeField()
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    class Meta:
        db_table = "appointments"
        verbose_name = "Lịch hẹn"
        verbose_name_plural = "Lịch hẹn"

    def __str__(self):
        return f"Appointment #{self.id} - {self.pet.name}"
