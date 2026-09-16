from types import SimpleNamespace

import pytest
from django.db import IntegrityError
from rest_framework_simplejwt.exceptions import TokenError

from src.common.exceptions import (
    BadRequestException,
    NotFoundException,
    PermissionDeniedException,
    UnauthorizedException,
)
from src.models import User
from src.services.user_service import UserService


pytestmark = pytest.mark.django_db


class FakeRefreshToken:
    access_token = "access-token"

    def __init__(self, user_id="1", blacklist=None):
        self.user_id = user_id
        self.blacklist = blacklist or (lambda: None)

    def __getitem__(self, key):
        if key == "user_id":
            return self.user_id
        raise KeyError(key)

    def __str__(self):
        return "refresh-token"


def test_login_returns_tokens_when_authenticate_succeeds(mocker):
    # Arrange
    user = SimpleNamespace(id=1, is_active=True)
    authenticate = mocker.patch("src.services.user_service.authenticate", return_value=user)
    refresh_token = mocker.patch("src.services.user_service.RefreshToken")
    refresh_token.for_user.return_value = FakeRefreshToken()

    # Act
    result = UserService.login({"username": "owner", "password": "password123"})

    # Assert
    authenticate.assert_called_once_with(username="owner", password="password123")
    refresh_token.for_user.assert_called_once_with(user)
    assert result == {
        "user": user,
        "access": "access-token",
        "refresh": "refresh-token",
    }


def test_login_rejects_invalid_credentials(mocker):
    # Arrange
    mocker.patch("src.services.user_service.authenticate", return_value=None)
    refresh_token = mocker.patch("src.services.user_service.RefreshToken")

    # Act / Assert
    with pytest.raises(UnauthorizedException):
        UserService.login({"username": "owner", "password": "wrong-password"})

    refresh_token.for_user.assert_not_called()


def test_login_rejects_inactive_user(mocker):
    # Arrange
    inactive_user = SimpleNamespace(id=1, is_active=False)
    mocker.patch("src.services.user_service.authenticate", return_value=inactive_user)
    refresh_token = mocker.patch("src.services.user_service.RefreshToken")

    # Act / Assert
    with pytest.raises(UnauthorizedException):
        UserService.login({"username": "owner", "password": "password123"})

    refresh_token.for_user.assert_not_called()


def test_refresh_access_token_returns_new_access_token(mocker):
    # Arrange
    token = SimpleNamespace(access_token="new-access-token")
    refresh_token = mocker.patch("src.services.user_service.RefreshToken", return_value=token)

    # Act
    result = UserService.refresh_access_token("valid-refresh-token")

    # Assert
    refresh_token.assert_called_once_with("valid-refresh-token")
    assert result == {"access": "new-access-token"}


def test_refresh_access_token_wraps_token_error(mocker):
    # Arrange
    mocker.patch(
        "src.services.user_service.RefreshToken",
        side_effect=TokenError("invalid token"),
    )

    # Act / Assert
    with pytest.raises(BadRequestException):
        UserService.refresh_access_token("invalid-refresh-token")


def test_logout_blacklists_token_when_user_matches(mocker):
    # Arrange
    blacklist = mocker.Mock()
    token = FakeRefreshToken(user_id="7", blacklist=blacklist)
    refresh_token = mocker.patch("src.services.user_service.RefreshToken", return_value=token)

    # Act
    UserService.logout_user(7, "valid-refresh-token")

    # Assert
    refresh_token.assert_called_once_with("valid-refresh-token")
    blacklist.assert_called_once_with()


def test_logout_rejects_refresh_token_for_another_user(mocker):
    # Arrange
    blacklist = mocker.Mock()
    token = FakeRefreshToken(user_id="99", blacklist=blacklist)
    mocker.patch("src.services.user_service.RefreshToken", return_value=token)

    # Act / Assert
    with pytest.raises(PermissionDeniedException):
        UserService.logout_user(7, "other-user-refresh-token")

    blacklist.assert_not_called()


def test_logout_wraps_token_error(mocker):
    # Arrange
    mocker.patch(
        "src.services.user_service.RefreshToken",
        side_effect=TokenError("invalid token"),
    )

    # Act / Assert
    with pytest.raises(BadRequestException):
        UserService.logout_user(7, "invalid-refresh-token")


def test_register_user_delegates_to_repository_with_password_removed(mocker):
    # Arrange
    user = SimpleNamespace(id=1, username="owner")
    create_user = mocker.patch(
        "src.services.user_service.UserRepository.create_user",
        return_value=user,
    )
    validated_data = {
        "username": "owner",
        "email": "owner@example.com",
        "password": "password123",
        "full_name": "Pet Owner",
    }

    # Act
    result = UserService.register_user(validated_data)

    # Assert
    assert result == user
    create_user.assert_called_once_with(
        password="password123",
        username="owner",
        email="owner@example.com",
        full_name="Pet Owner",
    )
    assert validated_data["password"] == "password123"


def test_register_user_wraps_integrity_error(mocker):
    # Arrange
    mocker.patch(
        "src.services.user_service.UserRepository.create_user",
        side_effect=IntegrityError("duplicate"),
    )

    # Act / Assert
    with pytest.raises(BadRequestException):
        UserService.register_user(
            {
                "username": "owner",
                "email": "owner@example.com",
                "password": "password123",
                "full_name": "Pet Owner",
            },
        )


def test_get_profile_returns_user_from_repository(mocker):
    # Arrange
    user = SimpleNamespace(id=1)
    get_by_id = mocker.patch(
        "src.services.user_service.UserRepository.get_by_id",
        return_value=user,
    )

    # Act
    result = UserService.get_profile(1)

    # Assert
    assert result == user
    get_by_id.assert_called_once_with(1)


def test_get_profile_rejects_missing_user(mocker):
    # Arrange
    mocker.patch("src.services.user_service.UserRepository.get_by_id", return_value=None)

    # Act / Assert
    with pytest.raises(NotFoundException):
        UserService.get_profile(999999)


def test_update_profile_updates_allowed_fields_and_saves(mocker):
    # Arrange
    user = SimpleNamespace(
        id=1,
        full_name="Old Name",
        phone="0900000000",
        address="Old Address",
    )
    save = mocker.patch("src.services.user_service.UserRepository.save", return_value=user)
    mocker.patch("src.services.user_service.UserRepository.get_by_id", return_value=user)

    # Act
    result = UserService.update_profile(
        1,
        {
            "full_name": "New Name",
            "phone": "0911111111",
            "address": "New Address",
        },
    )

    # Assert
    assert result == user
    assert user.full_name == "New Name"
    assert user.phone == "0911111111"
    assert user.address == "New Address"
    save.assert_called_once_with(user)


def test_change_password_checks_current_password_and_saves(mocker):
    # Arrange
    user = SimpleNamespace(
        id=1,
        check_password=mocker.Mock(return_value=True),
        set_password=mocker.Mock(),
    )
    mocker.patch("src.services.user_service.UserRepository.get_by_id", return_value=user)
    save = mocker.patch("src.services.user_service.UserRepository.save", return_value=user)

    # Act
    result = UserService.change_password(1, "old-password", "new-password")

    # Assert
    assert result == user
    user.check_password.assert_called_once_with("old-password")
    user.set_password.assert_called_once_with("new-password")
    save.assert_called_once_with(user)


def test_change_password_rejects_wrong_current_password(mocker):
    # Arrange
    user = SimpleNamespace(
        id=1,
        check_password=mocker.Mock(return_value=False),
        set_password=mocker.Mock(),
    )
    mocker.patch("src.services.user_service.UserRepository.get_by_id", return_value=user)
    save = mocker.patch("src.services.user_service.UserRepository.save")

    # Act / Assert
    with pytest.raises(BadRequestException):
        UserService.change_password(1, "wrong-password", "new-password")

    user.set_password.assert_not_called()
    save.assert_not_called()


def test_change_password_rejects_missing_user(mocker):
    # Arrange
    mocker.patch("src.services.user_service.UserRepository.get_by_id", return_value=None)

    # Act / Assert
    with pytest.raises(NotFoundException):
        UserService.change_password(999999, "old-password", "new-password")


def test_create_staff_assigns_clinic_and_staff_role(mocker):
    # Arrange
    clinic = SimpleNamespace(id=10)
    staff = SimpleNamespace(id=2, role=User.ROLE_CLINIC_STAFF, clinic=clinic)
    mocker.patch("src.services.user_service.ClinicRepository.get_by_id", return_value=clinic)
    create_user = mocker.patch(
        "src.services.user_service.UserRepository.create_user",
        return_value=staff,
    )

    # Act
    result = UserService.create_staff(
        {
            "username": "staff",
            "email": "staff@example.com",
            "password": "password123",
            "full_name": "Clinic Staff",
            "clinic_id": clinic.id,
        },
    )

    # Assert
    assert result == staff
    create_user.assert_called_once_with(
        password="password123",
        username="staff",
        email="staff@example.com",
        full_name="Clinic Staff",
        clinic=clinic,
        role=User.ROLE_CLINIC_STAFF,
    )


def test_create_staff_rejects_missing_clinic(mocker):
    # Arrange
    mocker.patch("src.services.user_service.ClinicRepository.get_by_id", return_value=None)

    # Act / Assert
    with pytest.raises(NotFoundException):
        UserService.create_staff(
            {
                "username": "staff",
                "email": "staff@example.com",
                "password": "password123",
                "full_name": "Clinic Staff",
                "clinic_id": 999999,
            },
        )


def test_update_staff_updates_fields_clinic_and_password(mocker):
    # Arrange
    clinic = SimpleNamespace(id=10)
    staff = SimpleNamespace(
        id=2,
        email="old-staff@example.com",
        full_name="Old Staff",
        phone="0900000000",
        address="Old Address",
        is_active=True,
        clinic=None,
        set_password=mocker.Mock(),
    )
    mocker.patch.object(UserService, "get_staff_detail", return_value=staff)
    mocker.patch("src.services.user_service.UserRepository.get_by_email", return_value=None)
    mocker.patch("src.services.user_service.ClinicRepository.get_by_id", return_value=clinic)
    save = mocker.patch("src.services.user_service.UserRepository.save", return_value=staff)

    # Act
    result = UserService.update_staff(
        staff.id,
        {
            "email": "new-staff@example.com",
            "full_name": "New Staff",
            "phone": "0911111111",
            "address": "New Address",
            "is_active": False,
            "clinic_id": clinic.id,
            "password": "new-password",
        },
    )

    # Assert
    assert result == staff
    assert staff.email == "new-staff@example.com"
    assert staff.full_name == "New Staff"
    assert staff.phone == "0911111111"
    assert staff.address == "New Address"
    assert staff.is_active is False
    assert staff.clinic == clinic
    staff.set_password.assert_called_once_with("new-password")
    save.assert_called_once_with(staff)


def test_update_staff_rejects_duplicate_email(mocker):
    # Arrange
    staff = SimpleNamespace(id=2, email="staff@example.com")
    existing_user = SimpleNamespace(id=3, email="staff@example.com")
    mocker.patch.object(UserService, "get_staff_detail", return_value=staff)
    mocker.patch(
        "src.services.user_service.UserRepository.get_by_email",
        return_value=existing_user,
    )
    save = mocker.patch("src.services.user_service.UserRepository.save")

    # Act / Assert
    with pytest.raises(BadRequestException):
        UserService.update_staff(staff.id, {"email": "staff@example.com"})

    save.assert_not_called()


def test_delete_staff_deactivates_and_saves_staff(mocker):
    # Arrange
    staff = SimpleNamespace(id=2, is_active=True)
    mocker.patch.object(UserService, "get_staff_detail", return_value=staff)
    save = mocker.patch("src.services.user_service.UserRepository.save", return_value=staff)

    # Act
    result = UserService.delete_staff(staff.id)

    # Assert
    assert result == staff
    assert staff.is_active is False
    save.assert_called_once_with(staff)
