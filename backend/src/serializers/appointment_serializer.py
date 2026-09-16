from django.utils import timezone
from rest_framework import serializers

from src.models import Appointment
from src.serializers.payment_serializer import PaymentSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    owner_full_name = serializers.CharField(source="owner.full_name", read_only=True)
    pet_name = serializers.CharField(source="pet.name", read_only=True)
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)
    medical_record_id = serializers.IntegerField(source="medical_record.id", read_only=True, allow_null=True)
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            "id",
            "owner",
            "owner_username",
            "owner_full_name",
            "pet",
            "pet_name",
            "clinic",
            "clinic_name",
            "service",
            "service_name",
            "appointment_time",
            "note",
            "status",
            "medical_record_id",
            "payment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "status", "created_at", "updated_at"]


class AppointmentCreateSerializer(serializers.Serializer):
    pet_id = serializers.IntegerField()
    clinic_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    appointment_time = serializers.DateTimeField()
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_appointment_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Thời gian đặt lịch phải lớn hơn thời điểm hiện tại.")
        return value


class AppointmentUpdateSerializer(serializers.Serializer):
    appointment_time = serializers.DateTimeField(required=False)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_appointment_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Thời gian đặt lịch phải lớn hơn thời điểm hiện tại.")
        return value
