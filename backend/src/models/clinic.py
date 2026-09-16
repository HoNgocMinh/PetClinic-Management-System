from django.db import models
from src.common.base_model import TimeStampedModel


class Clinic(TimeStampedModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "clinics"
        verbose_name = "Phòng khám"
        verbose_name_plural = "Phòng khám"

    def __str__(self):
        return self.name


class Service(TimeStampedModel):
    SERVICE_EXAM = "EXAM"
    SERVICE_GROOMING = "GROOMING"
    SERVICE_VACCINE = "VACCINE"
    SERVICE_OTHER = "OTHER"

    SERVICE_TYPE_CHOICES = [
        (SERVICE_EXAM, "Examination"),
        (SERVICE_GROOMING, "Grooming"),
        (SERVICE_VACCINE, "Vaccine"),
        (SERVICE_OTHER, "Other"),
    ]

    clinic = models.ForeignKey(
        "src.Clinic",
        on_delete=models.CASCADE,
        related_name="services"
    )
    name = models.CharField(max_length=100)
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPE_CHOICES,
        default=SERVICE_OTHER
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "services"
        verbose_name = "Dịch vụ"
        verbose_name_plural = "Dịch vụ"

    def __str__(self):
        return f"{self.name} - {self.clinic.name}"
