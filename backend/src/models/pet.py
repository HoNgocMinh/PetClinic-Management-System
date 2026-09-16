from django.conf import settings
from django.db import models
from src.common.base_model import TimeStampedModel


class Pet(TimeStampedModel):
    SPECIES_DOG = "DOG"
    SPECIES_CAT = "CAT"
    SPECIES_OTHER = "OTHER"

    SPECIES_CHOICES = [
        (SPECIES_DOG, "Dog"),
        (SPECIES_CAT, "Cat"),
        (SPECIES_OTHER, "Other"),
    ]

    GENDER_MALE = "MALE"
    GENDER_FEMALE = "FEMALE"

    GENDER_CHOICES = [
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pets"
    )
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    note = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "pets"
        verbose_name = "Thú cưng"
        verbose_name_plural = "Thú cưng"

    def __str__(self):
        return self.name
