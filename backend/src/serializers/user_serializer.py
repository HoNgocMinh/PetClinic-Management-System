from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from src.models import User


class UserSerializer(serializers.ModelSerializer):
    clinic_id = serializers.IntegerField(source="clinic.id", read_only=True)
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "phone",
            "address",
            "role",
            "clinic_id",
            "clinic_name",
            "is_active",
            "created_at",
            "updated_at",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        error_messages={
            "min_length": "Mật khẩu phải có ít nhất 6 ký tự.",
            "blank": "Mật khẩu không được để trống.",
        },
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "full_name",
            "phone",
            "address",
        ]

    def validate(self, attrs):
        user = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
            full_name=attrs.get("full_name"),
        )

        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc

        return attrs

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Tên đăng nhập đã tồn tại.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email đã tồn tại.")
        return value


class AdminStaffCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        error_messages={
            "min_length": "Mật khẩu phải có ít nhất 6 ký tự.",
            "blank": "Mật khẩu không được để trống.",
        },
    )
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    clinic_id = serializers.IntegerField()
    is_active = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        user = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
            full_name=attrs.get("full_name"),
            role=User.ROLE_CLINIC_STAFF,
        )

        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc

        return attrs

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Tên đăng nhập đã tồn tại.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email đã tồn tại.")
        return value

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Họ và tên không được để trống.")
        return value


class AdminStaffUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=6,
        error_messages={
            "min_length": "Mật khẩu phải có ít nhất 6 ký tự.",
            "blank": "Mật khẩu không được để trống.",
        },
    )
    full_name = serializers.CharField(max_length=255, required=False)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    clinic_id = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if "password" in attrs:
            user = User(
                username=self.instance.username if self.instance else "",
                email=attrs.get("email") or (self.instance.email if self.instance else ""),
                full_name=attrs.get("full_name") or (self.instance.full_name if self.instance else ""),
                role=User.ROLE_CLINIC_STAFF,
            )
            try:
                validate_password(attrs["password"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Họ và tên không được để trống.")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "phone", "address"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=6,
        error_messages={
            "min_length": "Mật khẩu mới phải có ít nhất 6 ký tự.",
            "blank": "Mật khẩu mới không được để trống.",
        },
    )
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": ["Mật khẩu xác nhận không khớp."]})

        user = self.context.get("user")
        try:
            validate_password(attrs["new_password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"new_password": list(exc.messages)}) from exc

        return attrs
