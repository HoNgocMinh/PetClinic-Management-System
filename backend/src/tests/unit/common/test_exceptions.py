import pytest
from rest_framework import status

from src.common.exceptions import (
    AppException,
    BadRequestException,
    BusinessException,
    ConflictException,
    NotFoundException,
    PermissionDeniedException,
    UnauthorizedException,
)


@pytest.mark.parametrize(
    ("exception_class", "expected_status", "expected_code"),
    [
        (BadRequestException, status.HTTP_400_BAD_REQUEST, "bad_request"),
        (BusinessException, status.HTTP_400_BAD_REQUEST, "business_error"),
        (UnauthorizedException, status.HTTP_401_UNAUTHORIZED, "unauthorized"),
        (PermissionDeniedException, status.HTTP_403_FORBIDDEN, "permission_denied"),
        (NotFoundException, status.HTTP_404_NOT_FOUND, "not_found"),
        (ConflictException, status.HTTP_409_CONFLICT, "conflict"),
    ],
)
def test_app_exception_subclasses_use_expected_status_and_code(
    exception_class,
    expected_status,
    expected_code,
):
    exc = exception_class("Custom message")

    assert exc.status_code == expected_status
    assert str(exc.detail) == "Custom message"
    assert exc.get_codes() == expected_code


def test_app_exception_allows_status_and_code_override():
    exc = AppException(
        "Service unavailable",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="service_unavailable",
    )

    assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert str(exc.detail) == "Service unavailable"
    assert exc.get_codes() == "service_unavailable"
