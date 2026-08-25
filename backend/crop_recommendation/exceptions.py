from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    Formats errors according to the Phase 4 specification:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "fields": { ... } // Optional
        }
    }
    """
    # Call REST framework's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Standard DRF ValidationError returns a dict of field errors or a list of general errors.
        # It's usually HTTP 400.
        if response.status_code == 400:
            error_payload = {
                "code": "VALIDATION_ERROR",
                "message": "One or more fields are invalid.",
                "fields": response.data
            }
        elif response.status_code == 404:
            error_payload = {
                "code": "NOT_FOUND",
                "message": "The requested resource was not found."
            }
        else:
            # Handle other standard DRF errors (e.g., 401, 403)
            error_payload = {
                "code": "API_ERROR",
                "message": str(exc)
            }

        response.data = {
            "success": False,
            "error": error_payload
        }
        return response

    # If response is None, it means it's an unhandled exception (HTTP 500).
    # Since we shouldn't expose internal server errors directly to the API,
    # we can format it nicely here. Note: in production, you might want 
    # to log this exception explicitly.
    import logging
    logger = logging.getLogger(__name__)
    logger.exception("Unhandled API Exception")

    return Response(
        {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred."
            }
        },
        status=500
    )
