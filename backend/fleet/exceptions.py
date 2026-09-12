import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Standardized JSON error responses for all API errors.
    Wraps DRF default handler output in a consistent envelope.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "error": {
                "status": response.status_code,
                "detail": response.data,
            }
        }
        response.data = error_data
        return response

    # Unhandled exceptions — return 500
    logger.exception("Unhandled exception in view", exc_info=exc)
    return Response(
        {
            "error": {
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": "Internal server error.",
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class BusinessLogicError(Exception):
    """Raised by service layer for domain rule violations."""

    def __init__(self, message: str, code: str = "business_logic_error"):
        self.message = message
        self.code = code
        super().__init__(message)
