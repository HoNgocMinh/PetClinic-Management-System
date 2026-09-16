import pytest
from rest_framework import status

from src.common.exceptions import BadRequestException
from src.controllers.user_controller import (
    ChangePasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView,
    RefreshTokenAPIView,
    RegisterAPIView,
    StaffAdminDetailAPIView,
    StaffAdminListCreateAPIView,
)
from src.tests.factories import AdminUserFactory, ClinicFactory, StaffUserFactory, UserFactory
from src.tests.unit.controllers.helpers import assert_success, make_request


pytestmark = pytest.mark.django_db


def test_user_controller_delegates_auth_profile_and_staff_flows(mocker):
    clinic = ClinicFactory()
    admin = AdminUserFactory()
    owner = UserFactory()
    staff = StaffUserFactory(clinic=clinic)

    mocker.patch("src.controllers.user_controller.UserService.register_user", return_value=owner)
    assert_success(
        RegisterAPIView().post(
            make_request(
                data={
                    "username": "controller_owner",
                    "email": "controller_owner@example.com",
                    "password": "StrongPass123!",
                    "full_name": "Controller Owner",
                },
            ),
        ),
        status.HTTP_201_CREATED,
    )

    mocker.patch(
        "src.controllers.user_controller.UserService.login",
        return_value={"user": owner, "access": "access", "refresh": "refresh"},
    )
    login_data = assert_success(
        LoginAPIView().post(make_request(data={"username": owner.username, "password": "secret"})),
    )
    assert login_data["access_token"] == "access"

    mocker.patch(
        "src.controllers.user_controller.UserService.refresh_access_token",
        return_value={"access": "new-access"},
    )
    refresh_data = assert_success(
        RefreshTokenAPIView().post(make_request(data={"refresh_token": "refresh"})),
    )
    assert refresh_data["access_token"] == "new-access"

    mocker.patch("src.controllers.user_controller.UserService.logout_user")
    assert_success(LogoutAPIView().post(make_request(owner, {"refresh_token": "refresh"})))

    mocker.patch("src.controllers.user_controller.UserService.get_profile", return_value=owner)
    assert_success(ProfileAPIView().get(make_request(owner)))

    mocker.patch("src.controllers.user_controller.UserService.update_profile", return_value=owner)
    assert_success(ProfileAPIView().put(make_request(owner, {"full_name": "New Name"})))

    change_password = mocker.patch("src.controllers.user_controller.UserService.change_password")
    assert_success(
        ChangePasswordAPIView().put(
            make_request(
                owner,
                {
                    "old_password": "OldPass123!",
                    "new_password": "NewPass123!",
                    "confirm_password": "NewPass123!",
                },
            ),
        ),
    )
    change_password.assert_called_once_with(owner.id, "OldPass123!", "NewPass123!")

    mocker.patch(
        "src.controllers.user_controller.UserService.get_staff_list",
        return_value=[staff],
    )
    assert_success(
        StaffAdminListCreateAPIView().get(
            make_request(admin, query_params={"clinic_id": str(clinic.id), "is_active": "true"}),
        ),
    )

    with pytest.raises(BadRequestException):
        StaffAdminListCreateAPIView().get(
            make_request(admin, query_params={"clinic_id": "abc"}),
        )

    mocker.patch("src.controllers.user_controller.UserService.create_staff", return_value=staff)
    assert_success(
        StaffAdminListCreateAPIView().post(
            make_request(
                admin,
                {
                    "username": "controller_staff",
                    "email": "controller_staff@example.com",
                    "password": "StrongPass123!",
                    "full_name": "Controller Staff",
                    "clinic_id": clinic.id,
                },
            ),
        ),
        status.HTTP_201_CREATED,
    )

    mocker.patch("src.controllers.user_controller.UserService.get_staff_detail", return_value=staff)
    assert_success(StaffAdminDetailAPIView().get(make_request(admin), staff.id))

    mocker.patch("src.controllers.user_controller.UserService.update_staff", return_value=staff)
    assert_success(
        StaffAdminDetailAPIView().put(
            make_request(admin, {"full_name": "Updated Staff"}),
            staff.id,
        ),
    )

    mocker.patch("src.controllers.user_controller.UserService.delete_staff", return_value=staff)
    assert_success(StaffAdminDetailAPIView().delete(make_request(admin), staff.id))
