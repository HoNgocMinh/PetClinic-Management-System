from rest_framework.permissions import BasePermission, SAFE_METHODS

from src.models import User


class BaseRolePermission(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        user = request.user
        return (
            bool(user)
            and user.is_authenticated
            and user.role in self.allowed_roles
        )


class IsAdminUserRole(BaseRolePermission):
    allowed_roles = (User.ROLE_ADMIN,)


class IsClinicStaffRole(BaseRolePermission):
    allowed_roles = (User.ROLE_CLINIC_STAFF,)


class IsPetOwnerRole(BaseRolePermission):
    allowed_roles = (User.ROLE_PET_OWNER,)


class IsAdminOrClinicStaffRole(BaseRolePermission):
    allowed_roles = (
        User.ROLE_ADMIN,
        User.ROLE_CLINIC_STAFF,
    )


class IsAdminOrPetOwnerRole(BaseRolePermission):
    allowed_roles = (
        User.ROLE_ADMIN,
        User.ROLE_PET_OWNER,
    )


class IsReadOnlyOrAdminRole(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        return bool(user) and user.is_authenticated and user.role == User.ROLE_ADMIN
