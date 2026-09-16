from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = "Có lỗi xảy ra."
        errors = None

        if isinstance(response.data, dict):
            if "detail" in response.data:
                message = response.data["detail"]
            else:
                message = "Dữ liệu không hợp lệ."
                errors = response.data
        elif isinstance(response.data, list):
            message = "Dữ liệu không hợp lệ."
            errors = response.data

        response.data = {
            "success": False,
            "message": message,
            "errors": errors,
        }

    return response
