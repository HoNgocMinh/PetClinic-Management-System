from rest_framework import serializers

from src.models import Clinic, Service


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = [
            "id",
            "name",
            "address",
            "phone",
            "email",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ClinicCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên phòng khám không được để trống.")
        return value

    def validate_address(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Địa chỉ không được để trống.")
        return value


class ClinicUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    address = serializers.CharField(max_length=255, required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên phòng khám không được để trống.")
        return value

    def validate_address(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Địa chỉ không được để trống.")
        return value


class ServiceSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "clinic",
            "clinic_name",
            "name",
            "service_type",
            "description",
            "price",
            "duration_minutes",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ServiceCreateSerializer(serializers.Serializer):
    clinic_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    service_type = serializers.ChoiceField(choices=Service.SERVICE_TYPE_CHOICES)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = serializers.IntegerField()

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên dịch vụ không được để trống.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Giá dịch vụ phải lớn hơn 0.")
        return value

    def validate_duration_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Thời lượng dịch vụ phải lớn hơn 0.")
        return value


class ServiceUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    service_type = serializers.ChoiceField(choices=Service.SERVICE_TYPE_CHOICES, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    duration_minutes = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên dịch vụ không được để trống.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Giá dịch vụ phải lớn hơn 0.")
        return value

    def validate_duration_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Thời lượng dịch vụ phải lớn hơn 0.")
        return value
