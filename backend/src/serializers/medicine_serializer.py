from rest_framework import serializers

from src.models import Medicine


class MedicineSerializer(serializers.ModelSerializer):
    clinic_id = serializers.IntegerField(source="clinic.id", read_only=True)
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)

    class Meta:
        model = Medicine
        fields = [
            "id",
            "clinic_id",
            "clinic_name",
            "name",
            "unit",
            "description",
            "stock_quantity",
            "price",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "clinic_id",
            "clinic_name",
            "created_at",
            "updated_at",
        ]


class MedicineCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    unit = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True)
    stock_quantity = serializers.IntegerField(required=False, min_value=0)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, min_value=0)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên thuốc không được để trống.")
        return value

    def validate_unit(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Đơn vị thuốc không được để trống.")
        return value


class MedicineUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=False)
    unit = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    stock_quantity = serializers.IntegerField(required=False, min_value=0)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, min_value=0)
    is_active = serializers.BooleanField(required=False)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên thuốc không được để trống.")
        return value

    def validate_unit(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Đơn vị thuốc không được để trống.")
        return value
