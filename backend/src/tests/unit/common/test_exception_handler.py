from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, ValidationError

from src.common.exception_handler import custom_exception_handler
from src.common.exceptions import BadRequestException


def test_custom_exception_handler_wraps_detail_errors():
    response = custom_exception_handler(NotFound("Missing pet"), {})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["success"] is False
    assert str(response.data["message"]) == "Missing pet"
    assert response.data["errors"] is None


def test_custom_exception_handler_wraps_field_validation_errors():
    response = custom_exception_handler(
        serializers.ValidationError({"name": ["This field is required."]}),
        {},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert response.data["errors"] == {"name": ["This field is required."]}


def test_custom_exception_handler_wraps_list_validation_errors():
    response = custom_exception_handler(ValidationError(["Invalid item."]), {})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert response.data["errors"] == ["Invalid item."]


def test_custom_exception_handler_wraps_app_exceptions():
    response = custom_exception_handler(BadRequestException("Bad request"), {})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "success": False,
        "message": "Bad request",
        "errors": None,
    }


def test_custom_exception_handler_returns_none_for_unhandled_exceptions():
    assert custom_exception_handler(ValueError("boom"), {}) is None
