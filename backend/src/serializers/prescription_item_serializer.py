from rest_framework import serializers

from src.models import PrescriptionItem


class PrescriptionItemSerializer(serializers.ModelSerializer):
    medicine_id = serializers.IntegerField(source="medicine.id", read_only=True)
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_unit = serializers.CharField(source="medicine.unit", read_only=True)

    class Meta:
        model = PrescriptionItem
        fields = [
            "id",
            "medicine_id",
            "medicine_name",
            "medicine_unit",
            "quantity",
            "dosage",
            "frequency",
            "duration_days",
            "instruction",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "medicine_id",
            "medicine_name",
            "medicine_unit",
            "created_at",
            "updated_at",
        ]


class PrescriptionItemCreateSerializer(serializers.Serializer):
    medicine_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    dosage = serializers.CharField(max_length=100)
    frequency = serializers.CharField(max_length=100)
    duration_days = serializers.IntegerField(min_value=1)
    instruction = serializers.CharField(required=False, allow_blank=True)

    def validate_dosage(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Liều dùng không được để trống.")
        return value

    def validate_frequency(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tần suất sử dụng không được để trống.")
        return value


class PrescriptionItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=False, min_value=1)
    dosage = serializers.CharField(max_length=100, required=False)
    frequency = serializers.CharField(max_length=100, required=False)
    duration_days = serializers.IntegerField(required=False, min_value=1)
    instruction = serializers.CharField(required=False, allow_blank=True)

    def validate_dosage(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Liều dùng không được để trống.")
        return value

    def validate_frequency(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tần suất sử dụng không được để trống.")
        return value
