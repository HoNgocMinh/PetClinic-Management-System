from rest_framework import serializers

from src.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    appointment_id = serializers.IntegerField(source="appointment.id", read_only=True)
    appointment_time = serializers.DateTimeField(source="appointment.appointment_time", read_only=True)
    pet_id = serializers.IntegerField(source="appointment.pet.id", read_only=True)
    pet_name = serializers.CharField(source="appointment.pet.name", read_only=True)
    service_id = serializers.IntegerField(source="appointment.service.id", read_only=True)
    service_name = serializers.CharField(source="appointment.service.name", read_only=True)
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)
    clinic_id = serializers.IntegerField(source="clinic.id", read_only=True)
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "appointment_id",
            "appointment_time",
            "pet_id",
            "pet_name",
            "service_id",
            "service_name",
            "owner_id",
            "owner_name",
            "clinic_id",
            "clinic_name",
            "amount",
            "method",
            "status",
            "paid_at",
            "transaction_code",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PaymentCreateSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField()
    method = serializers.ChoiceField(
        choices=Payment.METHOD_CHOICES,
        default=Payment.METHOD_VNPAY,
        required=False,
    )
    note = serializers.CharField(required=False, allow_blank=True)
