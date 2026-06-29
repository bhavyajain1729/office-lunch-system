"""
Custom DRF exception handler.

Ensures every error response sent to the React frontend has a consistent
shape: {"detail": "...", "errors": {...}} so the Axios interceptor and
UI toast/error components can rely on a single structure.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception (500) - don't leak internals to the client.
        return Response(
            {"detail": "Something went wrong. Please try again.", "errors": {}},
            status=500,
        )

    data = response.data

    # Normalize DRF's default error shapes into {detail, errors}.
    if isinstance(data, dict):
        detail = data.get("detail")
        if detail is None:
            # Field-level validation errors, e.g. {"email": ["This field is required."]}
            detail = "Validation failed."
            errors = data
        else:
            errors = {k: v for k, v in data.items() if k != "detail"}
    elif isinstance(data, list):
        detail = data[0] if data else "An error occurred."
        errors = {}
    else:
        detail = str(data)
        errors = {}

    response.data = {"detail": detail, "errors": errors}
    return response
