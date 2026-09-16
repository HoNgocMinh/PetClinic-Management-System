from rest_framework import serializers

from src.models import Prescription
from src.serializers.prescription_item_serializer import PrescriptionItemSerializer


class PrescriptionSerializer(serializers.ModelSerializer):
    medical_record_id = serializers.IntegerField(source="medical_record.id", read_only=True)
    clinic_id = serializers.IntegerField(source="clinic.id", read_only=True)
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)
    staff_id = serializers.IntegerField(source="staff.id", read_only=True)
    staff_name = serializers.CharField(source="staff.full_name", read_only=True)
    items = PrescriptionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id",
            "medical_record_id",
            "clinic_id",
            "clinic_name",
            "staff_id",
            "staff_name",
            "note",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "medical_record_id",
            "clinic_id",
            "clinic_name",
            "staff_id",
            "staff_name",
            "items",
            "created_at",
            "updated_at",
        ]


class PrescriptionCreateSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True)


class PrescriptionUpdateSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True)
