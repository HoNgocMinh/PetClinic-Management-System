import pytest

from src.serializers.medicine_serializer import MedicineCreateSerializer, MedicineUpdateSerializer
from src.tests.unit.serializers.helpers import assert_validation_error


pytestmark = pytest.mark.django_db


def test_medicine_serializers_validate_name_and_unit():
    create_serializer = MedicineCreateSerializer()
    update_serializer = MedicineUpdateSerializer()

    assert create_serializer.validate_name(" Vitamin ") == "Vitamin"
    assert create_serializer.validate_unit(" tablet ") == "tablet"
    assert update_serializer.validate_name(" Antibiotic ") == "Antibiotic"
    assert update_serializer.validate_unit(" ml ") == "ml"

    for callable_ in [
        create_serializer.validate_name,
        create_serializer.validate_unit,
        update_serializer.validate_name,
        update_serializer.validate_unit,
    ]:
        assert_validation_error(callable_, "   ")

    serializer = MedicineCreateSerializer(
        data={
            "name": "Vitamin",
            "unit": "tablet",
            "description": "",
            "stock_quantity": 10,
            "price": "5000.00",
        },
    )
    assert serializer.is_valid(), serializer.errors
