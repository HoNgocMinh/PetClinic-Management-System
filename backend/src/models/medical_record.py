from django.conf import settings
from django.db import models

from src.common.base_model import TimeStampedModel


class MedicalRecord(TimeStampedModel):
    appointment = models.OneToOneField(
        "src.Appointment",
        on_delete=models.CASCADE,
        related_name="medical_record",
    )
    pet = models.ForeignKey(
        "src.Pet",
        on_delete=models.CASCADE,
        related_name="medical_records",
    )
    clinic = models.ForeignKey(
        "src.Clinic",
        on_delete=models.CASCADE,
        related_name="medical_records",
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_medical_records",
    )
    symptoms = models.TextField()
    diagnosis = models.TextField()
    treatment = models.TextField(blank=True)
    note = models.TextField(blank=True)

    class Meta:
        db_table = "medical_records"
        ordering = ["-created_at"]
        verbose_name = "Hồ sơ bệnh án"
        verbose_name_plural = "Hồ sơ bệnh án"

    def __str__(self):
        return f"Medical record #{self.id} - Appointment #{self.appointment_id}"
