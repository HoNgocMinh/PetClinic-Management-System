from django.db import models

from src.common.base_model import TimeStampedModel


class Medicine(TimeStampedModel):
    clinic = models.ForeignKey(
        "src.Clinic",
        on_delete=models.CASCADE,
        related_name="medicines",
    )
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "medicines"
        ordering = ["name"]
        unique_together = ("clinic", "name")
        verbose_name = "Thuốc"
        verbose_name_plural = "Thuốc"

    def __str__(self):
        return f"{self.name} - {self.clinic.name}"
