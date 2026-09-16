from django.db import models

from src.common.base_model import TimeStampedModel


class PrescriptionItem(TimeStampedModel):
    prescription = models.ForeignKey(
        "src.Prescription",
        on_delete=models.CASCADE,
        related_name="items",
    )
    medicine = models.ForeignKey(
        "src.Medicine",
        on_delete=models.PROTECT,
        related_name="prescription_items",
    )
    quantity = models.PositiveIntegerField()
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField()
    instruction = models.TextField(blank=True)

    class Meta:
        db_table = "prescription_items"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["prescription", "medicine"],
                name="unique_prescription_medicine_item",
            ),
        ]
        verbose_name = "Chi tiết đơn thuốc"
        verbose_name_plural = "Chi tiết đơn thuốc"

    def __str__(self):
        return f"{self.medicine.name} - Prescription #{self.prescription_id}"
