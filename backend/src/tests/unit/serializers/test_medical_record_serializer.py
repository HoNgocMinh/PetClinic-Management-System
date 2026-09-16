import pytest

from src.serializers.medical_record_serializer import (
    MedicalRecordCreateSerializer,
    MedicalRecordUpdateSerializer,
)
from src.tests.unit.serializers.helpers import assert_validation_error


pytestmark = pytest.mark.django_db


def test_medical_record_serializers_validate_text_fields():
    create_serializer = MedicalRecordCreateSerializer()
    update_serializer = MedicalRecordUpdateSerializer()

    assert create_serializer.validate_symptoms(" Cough ") == "Cough"
    assert create_serializer.validate_diagnosis(" Cold ") == "Cold"
    assert update_serializer.validate_symptoms(" Fever ") == "Fever"
    assert update_serializer.validate_diagnosis(" Flu ") == "Flu"

    for callable_ in [
        create_serializer.validate_symptoms,
        create_serializer.validate_diagnosis,
        update_serializer.validate_symptoms,
        update_serializer.validate_diagnosis,
    ]:
        assert_validation_error(callable_, "   ")

    serializer = MedicalRecordCreateSerializer(
        data={
            "symptoms": "Cough",
            "diagnosis": "Cold",
            "treatment": "",
            "note": "",
        },
    )
    assert serializer.is_valid(), serializer.errors
