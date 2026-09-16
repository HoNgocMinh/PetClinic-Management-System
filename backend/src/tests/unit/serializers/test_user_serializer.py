import pytest
from django.core.exceptions import ValidationError as DjangoValidationError

from src.serializers.user_serializer import (
    AdminStaffCreateSerializer,
    AdminStaffUpdateSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
)
from src.tests.factories import StaffUserFactory, UserFactory
from src.tests.unit.serializers.helpers import assert_validation_error


pytestmark = pytest.mark.django_db


def test_user_auth_and_profile_serializers_accept_valid_payloads(mocker):
    mocker.patch("src.serializers.user_serializer.validate_password")

    register_serializer = RegisterSerializer(
        data={
            "username": "new_owner",
            "email": "new_owner@example.com",
            "password": "StrongPass123!",
            "full_name": "New Owner",
            "phone": "",
            "address": "",
        },
    )
    assert register_serializer.is_valid(), register_serializer.errors

    staff_serializer = AdminStaffCreateSerializer(
        data={
            "username": "new_staff",
            "email": "new_staff@example.com",
            "password": "StrongPass123!",
            "full_name": " Clinic Staff ",
            "phone": "",
            "address": "",
            "clinic_id": 1,
        },
    )
    assert staff_serializer.is_valid(), staff_serializer.errors
    assert staff_serializer.validated_data["full_name"] == "Clinic Staff"

    assert LoginSerializer(data={"username": "owner", "password": "secret"}).is_valid()
    assert LogoutSerializer(data={"refresh_token": "token"}).is_valid()
    assert RefreshTokenSerializer(data={"refresh_token": "token"}).is_valid()
    assert UpdateProfileSerializer(data={"full_name": "Owner"}, partial=True).is_valid()
    assert ChangePasswordSerializer(
        data={
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
        },
        context={"user": None},
    ).is_valid()


def test_user_serializers_reject_duplicates_and_invalid_values(mocker):
    existing_user = UserFactory(username="taken_owner", email="taken@example.com")
    existing_staff = StaffUserFactory(username="taken_staff", email="taken_staff@example.com")

    register_serializer = RegisterSerializer()
    staff_create_serializer = AdminStaffCreateSerializer()
    staff_update_serializer = AdminStaffUpdateSerializer(instance=existing_staff)

    assert_validation_error(register_serializer.validate_username, existing_user.username)
    assert_validation_error(register_serializer.validate_email, existing_user.email)
    assert_validation_error(staff_create_serializer.validate_username, existing_staff.username)
    assert_validation_error(staff_create_serializer.validate_email, existing_staff.email)
    assert_validation_error(staff_create_serializer.validate_full_name, "   ")
    assert_validation_error(staff_update_serializer.validate_full_name, "   ")

    mocker.patch(
        "src.serializers.user_serializer.validate_password",
        side_effect=DjangoValidationError(["too weak"]),
    )

    register_with_bad_password = RegisterSerializer(
        data={
            "username": "weak_owner",
            "email": "weak_owner@example.com",
            "password": "weak",
            "full_name": "Weak Owner",
        },
    )
    assert not register_with_bad_password.is_valid()
    assert "password" in register_with_bad_password.errors

    create_with_bad_password = AdminStaffCreateSerializer(
        data={
            "username": "weak_staff",
            "email": "weak_staff@example.com",
            "password": "weak",
            "full_name": "Weak Staff",
            "clinic_id": 1,
        },
    )
    assert not create_with_bad_password.is_valid()
    assert "password" in create_with_bad_password.errors

    update_with_bad_password = AdminStaffUpdateSerializer(
        instance=existing_staff,
        data={"password": "weak"},
        partial=True,
    )
    assert not update_with_bad_password.is_valid()
    assert "password" in update_with_bad_password.errors

    change_with_mismatched_confirmation = ChangePasswordSerializer(
        data={
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "confirm_password": "DifferentPass123!",
        },
        context={"user": existing_user},
    )
    assert not change_with_mismatched_confirmation.is_valid()
    assert "confirm_password" in change_with_mismatched_confirmation.errors

    change_with_bad_password = ChangePasswordSerializer(
        data={
            "old_password": "OldPass123!",
            "new_password": "weak",
            "confirm_password": "weak",
        },
        context={"user": existing_user},
    )
    assert not change_with_bad_password.is_valid()
    assert "new_password" in change_with_bad_password.errors
