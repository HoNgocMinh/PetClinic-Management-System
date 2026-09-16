from rest_framework import status
from rest_framework.exceptions import APIException


class AppException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Có lỗi xảy ra."
    default_code = "app_exception"

    def __init__(self, message=None, status_code=None, code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail=message or self.default_detail, code=code or self.default_code)


class BadRequestException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Yêu cầu không hợp lệ."
    default_code = "bad_request"


class BusinessException(BadRequestException):
    default_detail = "Thao tác không hợp lệ."
    default_code = "business_error"


class UnauthorizedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Bạn không có quyền truy cập."
    default_code = "unauthorized"


class PermissionDeniedException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Bạn không có quyền thực hiện hành động này."
    default_code = "permission_denied"


class NotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Không tìm thấy dữ liệu."
    default_code = "not_found"


class ConflictException(AppException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Dữ liệu bị xung đột."
    default_code = "conflict"
