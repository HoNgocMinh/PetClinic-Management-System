from rest_framework import status

from src.common.responses import error_response, success_response


def test_success_response_returns_standard_success_envelope():
    response = success_response(
        data={"id": 1},
        message="Created",
        status_code=status.HTTP_201_CREATED,
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {
        "success": True,
        "message": "Created",
        "data": {"id": 1},
    }


def test_error_response_returns_standard_error_envelope():
    response = error_response(
        message="Invalid payload",
        errors={"name": ["This field is required."]},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.data == {
        "success": False,
        "message": "Invalid payload",
        "errors": {"name": ["This field is required."]},
    }
