from rest_framework import serializers

from src.models import MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    appointment_id = serializers.IntegerField(source="appointment.id", read_only=True)
    pet_id = serializers.IntegerField(source="pet.id", read_only=True)
    pet_name = serializers.CharField(source="pet.name", read_only=True)
    clinic_id = serializers.IntegerField(source="clinic.id", read_only=True)
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)
    staff_id = serializers.IntegerField(source="staff.id", read_only=True)
    staff_name = serializers.CharField(source="staff.full_name", read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "appointment_id",
            "pet_id",
            "pet_name",
            "clinic_id",
            "clinic_name",
            "staff_id",
            "staff_name",
            "symptoms",
            "diagnosis",
            "treatment",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "appointment_id",
            "pet_id",
            "pet_name",
            "clinic_id",
            "clinic_name",
            "staff_id",
            "staff_name",
            "created_at",
            "updated_at",
        ]


class MedicalRecordCreateSerializer(serializers.Serializer):
    symptoms = serializers.CharField()
    diagnosis = serializers.CharField()
    treatment = serializers.CharField(required=False, allow_blank=True)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_symptoms(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Triệu chứng không được để trống.")
        return value

    def validate_diagnosis(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Chẩn đoán không được để trống.")
        return value


class MedicalRecordUpdateSerializer(serializers.Serializer):
    symptoms = serializers.CharField(required=False)
    diagnosis = serializers.CharField(required=False)
    treatment = serializers.CharField(required=False, allow_blank=True)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_symptoms(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Triệu chứng không được để trống.")
        return value

    def validate_diagnosis(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Chẩn đoán không được để trống.")
        return value
