from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.common.exceptions import BadRequestException
from src.common.permissions import IsAdminUserRole
from src.common.responses import success_response
from src.serializers.user_serializer import (
    AdminStaffCreateSerializer,
    AdminStaffUpdateSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from src.services.user_service import UserService


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.register_user(serializer.validated_data)
        output = UserSerializer(user)
        return success_response(
            data=output.data,
            message="Đăng ký thành công.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = UserService.login(serializer.validated_data)
        output = UserSerializer(result["user"])

        return success_response(
            data={
                "user": output.data,
                "access_token": result["access"],
                "refresh_token": result["refresh"],
            },
            message="Đăng nhập thành công.",
            status_code=status.HTTP_200_OK,
        )


class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = UserService.refresh_access_token(serializer.validated_data["refresh_token"])
        return success_response(
            data={"access_token": result["access"]},
            message="Làm mới access token thành công.",
            status_code=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        UserService.logout_user(request.user.id, serializer.validated_data["refresh_token"])
        return success_response(
            data=None,
            message="Đăng xuất thành công.",
            status_code=status.HTTP_200_OK,
        )


class ProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = UserService.get_profile(request.user.id)
        serializer = UserSerializer(user)
        return success_response(
            data=serializer.data,
            message="Lấy thông tin cá nhân thành công.",
            status_code=status.HTTP_200_OK,
        )

    def put(self, request):
        serializer = UpdateProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = UserService.update_profile(request.user.id, serializer.validated_data)
        output = UserSerializer(user)
        return success_response(
            data=output.data,
            message="Cập nhật hồ sơ thành công.",
            status_code=status.HTTP_200_OK,
        )


class ChangePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"user": request.user})
        serializer.is_valid(raise_exception=True)

        UserService.change_password(
            request.user.id,
            serializer.validated_data["old_password"],
            serializer.validated_data["new_password"],
        )
        return success_response(
            data=None,
            message="Đổi mật khẩu thành công.",
            status_code=status.HTTP_200_OK,
        )


class StaffAdminListCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        clinic_id = request.query_params.get("clinic_id")
        is_active_param = request.query_params.get("is_active")

        parsed_clinic_id = None
        if clinic_id:
            try:
                parsed_clinic_id = int(clinic_id)
            except ValueError as exc:
                raise BadRequestException("clinic_id phải là số nguyên hợp lệ.") from exc

        parsed_is_active = None
        if is_active_param is not None:
            parsed_is_active = is_active_param.strip().lower() in {"1", "true", "yes"}

        staff_list = UserService.get_staff_list(
            clinic_id=parsed_clinic_id,
            is_active=parsed_is_active,
        )
        serializer = UserSerializer(staff_list, many=True)
        return success_response(serializer.data, "Lấy danh sách nhân viên thành công.")

    def post(self, request):
        serializer = AdminStaffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff = UserService.create_staff(serializer.validated_data)
        output = UserSerializer(staff)
        return success_response(
            output.data,
            "Tạo nhân viên thành công.",
            status.HTTP_201_CREATED,
        )


class StaffAdminDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserRole]

    def get(self, request, staff_id):
        staff = UserService.get_staff_detail(staff_id)
        serializer = UserSerializer(staff)
        return success_response(serializer.data, "Lấy chi tiết nhân viên thành công.")

    def put(self, request, staff_id):
        staff = UserService.get_staff_detail(staff_id)
        serializer = AdminStaffUpdateSerializer(staff, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        staff = UserService.update_staff(staff_id, serializer.validated_data)
        output = UserSerializer(staff)
        return success_response(output.data, "Cập nhật nhân viên thành công.")

    def delete(self, request, staff_id):
        staff = UserService.delete_staff(staff_id)
        output = UserSerializer(staff)
        return success_response(output.data, "Khóa nhân viên thành công.")
