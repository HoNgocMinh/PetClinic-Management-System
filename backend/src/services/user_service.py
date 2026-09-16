from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from src.common.exceptions import (
    BadRequestException,
    NotFoundException,
    PermissionDeniedException,
    UnauthorizedException,
)
from src.models import User
from src.repositories.clinic_repository import ClinicRepository
from src.repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    def register_user(validated_data):
        user_data = validated_data.copy()
        password = user_data.pop("password")

        try:
            with transaction.atomic():
                return UserRepository.create_user(password=password, **user_data)
        except IntegrityError as exc:
            raise BadRequestException("Tên đăng nhập hoặc email đã tồn tại.") from exc

    @staticmethod
    def login(validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        user = authenticate(username=username, password=password)

        if not user:
            raise UnauthorizedException("Tên đăng nhập hoặc mật khẩu không chính xác.")

        if not user.is_active:
            raise UnauthorizedException("Tài khoản đã bị khóa.")

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def logout_user(user_id: int, refresh_token: str):
        try:
            token = RefreshToken(refresh_token)

            if str(token["user_id"]) != str(user_id):
                raise PermissionDeniedException("Bạn không thể đăng xuất phiên của người dùng khác.")

            token.blacklist()
        except TokenError as exc:
            raise BadRequestException("Refresh token không hợp lệ hoặc đã hết hạn.") from exc

    @staticmethod
    def refresh_access_token(refresh_token: str):
        try:
            token = RefreshToken(refresh_token)
            return {"access": str(token.access_token)}
        except TokenError as exc:
            raise BadRequestException("Refresh token không hợp lệ hoặc đã hết hạn.") from exc

    @staticmethod
    def get_profile(user_id: int):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Không tìm thấy người dùng.")
        return user

    @staticmethod
    def update_profile(user_id: int, data):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Không tìm thấy người dùng.")

        user.full_name = data.get("full_name", user.full_name)
        user.phone = data.get("phone", user.phone)
        user.address = data.get("address", user.address)
        return UserRepository.save(user)

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Không tìm thấy người dùng.")

        if not user.check_password(old_password):
            raise BadRequestException("Mật khẩu hiện tại không chính xác.")

        user.set_password(new_password)
        return UserRepository.save(user)

    @staticmethod
    def get_staff_list(clinic_id=None, is_active=None):
        return UserRepository.get_staff_list(clinic_id=clinic_id, is_active=is_active)

    @staticmethod
    def create_staff(validated_data):
        clinic = ClinicRepository.get_by_id(validated_data["clinic_id"])
        if not clinic:
            raise NotFoundException("Không tìm thấy phòng khám.")

        user_data = validated_data.copy()
        password = user_data.pop("password")
        user_data["clinic"] = clinic
        user_data["role"] = User.ROLE_CLINIC_STAFF
        user_data.pop("clinic_id", None)

        try:
            with transaction.atomic():
                return UserRepository.create_user(password=password, **user_data)
        except IntegrityError as exc:
            raise BadRequestException("Tên đăng nhập hoặc email đã tồn tại.") from exc

    @staticmethod
    def get_staff_detail(staff_id: int):
        user = UserRepository.get_by_id(staff_id)
        if not user or user.role != User.ROLE_CLINIC_STAFF:
            raise NotFoundException("Không tìm thấy nhân viên.")
        return user

    @staticmethod
    def update_staff(staff_id: int, validated_data):
        user = UserService.get_staff_detail(staff_id)

        if "email" in validated_data:
            existing_user = UserRepository.get_by_email(validated_data["email"])
            if existing_user and existing_user.id != user.id:
                raise BadRequestException("Email đã tồn tại.")
            user.email = validated_data["email"]

        if "full_name" in validated_data:
            user.full_name = validated_data["full_name"]
        if "phone" in validated_data:
            user.phone = validated_data["phone"]
        if "address" in validated_data:
            user.address = validated_data["address"]
        if "is_active" in validated_data:
            user.is_active = validated_data["is_active"]
        if "clinic_id" in validated_data:
            clinic = ClinicRepository.get_by_id(validated_data["clinic_id"])
            if not clinic:
                raise NotFoundException("Không tìm thấy phòng khám.")
            user.clinic = clinic
        if "password" in validated_data:
            user.set_password(validated_data["password"])

        return UserRepository.save(user)

    @staticmethod
    def delete_staff(staff_id: int):
        user = UserService.get_staff_detail(staff_id)
        user.is_active = False
        return UserRepository.save(user)
