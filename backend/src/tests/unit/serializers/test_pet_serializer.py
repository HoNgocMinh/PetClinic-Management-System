from datetime import date, timedelta

import pytest

from src.models import Pet
from src.serializers.pet_serializer import PetCreateSerializer, PetUpdateSerializer
from src.tests.unit.serializers.helpers import assert_validation_error


pytestmark = pytest.mark.django_db


def test_pet_serializers_validate_name_birth_date_and_weight():
    create_serializer = PetCreateSerializer()
    update_serializer = PetUpdateSerializer()
    today = date.today()
    tomorrow = today + timedelta(days=1)

    assert create_serializer.validate_name(" Milu ") == "Milu"
    assert update_serializer.validate_name(" Mimi ") == "Mimi"
    assert create_serializer.validate_birth_date(today) == today
    assert update_serializer.validate_birth_date(today) == today
    assert create_serializer.validate_weight(1) == 1
    assert update_serializer.validate_weight(2) == 2

    assert_validation_error(create_serializer.validate_name, "   ")
    assert_validation_error(update_serializer.validate_name, "   ")
    assert_validation_error(create_serializer.validate_birth_date, tomorrow)
    assert_validation_error(update_serializer.validate_birth_date, tomorrow)
    assert_validation_error(create_serializer.validate_weight, 0)
    assert_validation_error(update_serializer.validate_weight, 0)

    payload = {
        "name": "Milu",
        "species": Pet.SPECIES_DOG,
        "breed": "",
        "gender": Pet.GENDER_MALE,
        "birth_date": today,
        "weight": "4.50",
        "note": "",
    }
    serializer = PetCreateSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors
