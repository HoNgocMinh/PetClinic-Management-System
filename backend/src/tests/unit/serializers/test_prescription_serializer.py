import pytest

from src.serializers.prescription_item_serializer import (
    PrescriptionItemCreateSerializer,
    PrescriptionItemUpdateSerializer,
)
from src.serializers.prescription_serializer import (
    PrescriptionCreateSerializer,
    PrescriptionUpdateSerializer,
)
from src.tests.unit.serializers.helpers import assert_validation_error


pytestmark = pytest.mark.django_db


def test_prescription_serializers_validate_items_and_allow_blank_note():
    create_item = PrescriptionItemCreateSerializer()
    update_item = PrescriptionItemUpdateSerializer()

    assert create_item.validate_dosage(" 1 tablet ") == "1 tablet"
    assert create_item.validate_frequency(" twice daily ") == "twice daily"
    assert update_item.validate_dosage(" 2 ml ") == "2 ml"
    assert update_item.validate_frequency(" once daily ") == "once daily"

    for callable_ in [
        create_item.validate_dosage,
        create_item.validate_frequency,
        update_item.validate_dosage,
        update_item.validate_frequency,
    ]:
        assert_validation_error(callable_, "   ")

    item_serializer = PrescriptionItemCreateSerializer(
        data={
            "medicine_id": 1,
            "quantity": 1,
            "dosage": "1 tablet",
            "frequency": "twice daily",
            "duration_days": 5,
            "instruction": "",
        },
    )
    assert item_serializer.is_valid(), item_serializer.errors

    assert PrescriptionCreateSerializer(data={"note": ""}).is_valid()
    assert PrescriptionUpdateSerializer(data={"note": ""}).is_valid()
