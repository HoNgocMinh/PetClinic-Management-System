from datetime import date

from rest_framework import serializers

from src.models import Pet


class PetSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Pet
        fields = [
            "id",
            "owner",
            "owner_username",
            "name",
            "species",
            "breed",
            "gender",
            "birth_date",
            "weight",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "created_at", "updated_at"]


class PetCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    species = serializers.ChoiceField(choices=Pet.SPECIES_CHOICES)
    breed = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=Pet.GENDER_CHOICES)
    birth_date = serializers.DateField(required=False)
    weight = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên thú cưng không được để trống.")
        return value

    def validate_birth_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Ngày sinh không được lớn hơn ngày hiện tại.")
        return value

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cân nặng phải lớn hơn 0.")
        return value


class PetUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    species = serializers.ChoiceField(choices=Pet.SPECIES_CHOICES, required=False)
    breed = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=Pet.GENDER_CHOICES, required=False)
    birth_date = serializers.DateField(required=False)
    weight = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên thú cưng không được để trống.")
        return value

    def validate_birth_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Ngày sinh không được lớn hơn ngày hiện tại.")
        return value

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cân nặng phải lớn hơn 0.")
        return value
