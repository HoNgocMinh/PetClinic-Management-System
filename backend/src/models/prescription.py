from django.conf import settings
from django.db import models

from src.common.base_model import TimeStampedModel


class Prescription(TimeStampedModel):
    medical_record = models.OneToOneField(
        "src.MedicalRecord",
        on_delete=models.CASCADE,
        related_name="prescription",
    )
    clinic = models.ForeignKey(
        "src.Clinic",
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_prescriptions",
    )
    note = models.TextField(blank=True)

    class Meta:
        db_table = "prescriptions"
        ordering = ["-created_at"]
        verbose_name = "Đơn thuốc"
        verbose_name_plural = "Đơn thuốc"

    def __str__(self):
        return f"Prescription #{self.id} - Medical Record #{self.medical_record_id}"
