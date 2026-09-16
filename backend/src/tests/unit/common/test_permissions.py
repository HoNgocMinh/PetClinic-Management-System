from types import SimpleNamespace

import pytest

from src.common.permissions import (
    BaseRolePermission,
    IsAdminOrClinicStaffRole,
    IsAdminOrPetOwnerRole,
    IsAdminUserRole,
    IsClinicStaffRole,
    IsPetOwnerRole,
    IsReadOnlyOrAdminRole,
)
from src.models import User


def request_with(user=None, method="GET"):
    return SimpleNamespace(user=user, method=method)


def user_with(role, is_authenticated=True):
    return SimpleNamespace(role=role, is_authenticated=is_authenticated)


@pytest.mark.parametrize(
    ("permission_class", "allowed_role"),
    [
        (IsAdminUserRole, User.ROLE_ADMIN),
        (IsClinicStaffRole, User.ROLE_CLINIC_STAFF),
        (IsPetOwnerRole, User.ROLE_PET_OWNER),
    ],
)
def test_single_role_permissions_allow_only_the_configured_role(
    permission_class,
    allowed_role,
):
    permission = permission_class()

    assert permission.has_permission(request_with(user_with(allowed_role)), None) is True
    assert permission.has_permission(request_with(user_with("OTHER_ROLE")), None) is False
    assert permission.has_permission(request_with(user_with(allowed_role, False)), None) is False
    assert permission.has_permission(request_with(None), None) is False


def test_combined_role_permissions_allow_each_configured_role():
    assert IsAdminOrClinicStaffRole().has_permission(
        request_with(user_with(User.ROLE_ADMIN)),
        None,
    )
    assert IsAdminOrClinicStaffRole().has_permission(
        request_with(user_with(User.ROLE_CLINIC_STAFF)),
        None,
    )
    assert not IsAdminOrClinicStaffRole().has_permission(
        request_with(user_with(User.ROLE_PET_OWNER)),
        None,
    )

    assert IsAdminOrPetOwnerRole().has_permission(
        request_with(user_with(User.ROLE_ADMIN)),
        None,
    )
    assert IsAdminOrPetOwnerRole().has_permission(
        request_with(user_with(User.ROLE_PET_OWNER)),
        None,
    )
    assert not IsAdminOrPetOwnerRole().has_permission(
        request_with(user_with(User.ROLE_CLINIC_STAFF)),
        None,
    )


def test_base_role_permission_denies_when_no_roles_are_configured():
    assert not BaseRolePermission().has_permission(
        request_with(user_with(User.ROLE_ADMIN)),
        None,
    )


def test_read_only_or_admin_role_allows_safe_methods_for_any_request():
    permission = IsReadOnlyOrAdminRole()

    for method in ["GET", "HEAD", "OPTIONS"]:
        assert permission.has_permission(request_with(None, method), None) is True


def test_read_only_or_admin_role_requires_admin_for_write_methods():
    permission = IsReadOnlyOrAdminRole()

    assert permission.has_permission(
        request_with(user_with(User.ROLE_ADMIN), "POST"),
        None,
    ) is True
    assert permission.has_permission(
        request_with(user_with(User.ROLE_PET_OWNER), "POST"),
        None,
    ) is False
    assert permission.has_permission(request_with(None, "POST"), None) is False
