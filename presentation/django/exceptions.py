### WIP!!!
# TO BE CHECKED / INTEGRATED !!!!

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from application.exceptions import (
    RunNotFoundError,
    ModelNotFoundError,
    RunAlreadyStartedError,
    ParametersNotFoundError,
    DatabaseError,
)

# Exception map → (http_status, error_code)
EXCEPTION_MAP = {
    RunNotFoundError:        (status.HTTP_404_NOT_FOUND,            "run_not_found"),
    ModelNotFoundError:      (status.HTTP_404_NOT_FOUND,            "model_not_found"),
    ParametersNotFoundError: (status.HTTP_404_NOT_FOUND,            "parameters_not_found"),
    RunAlreadyStartedError:  (status.HTTP_409_CONFLICT,             "run_already_started"),
    DatabaseError:           (status.HTTP_503_SERVICE_UNAVAILABLE,  "database_error"),
}

def custom_exception_handler(exc, context):

    # 1. DRF manages the standard exceptions (ValidationError, NotFound, etc.)
    response = exception_handler(exc, context)
    if response is not None:
        return response

    # 2. Manage custom exceptions defined in the application
    for exc_class, (http_status, error_code) in EXCEPTION_MAP.items():
        if isinstance(exc, exc_class):
            return Response(
                {"error": error_code, "detail": str(exc)},
                status=http_status,
            )

    # 3. Safety net — something completely unexpected
    return Response(
        {"error": "internal_error", "detail": "Internal server error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )