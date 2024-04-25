import logging

from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exception, context):
    """
    Custom exception handler for Django Rest Framework that adds
    the `status_code` to the response body, renames the `detail` key to
    `message`, and `non_field_errors` to `data`.

    This mode of exception handling is inspired by the JSend specification
    for the structure of JSON API responses.

    See: https://github.com/omniti-labs/jsend
    """
    response = exception_handler(exception, context)
    handlers = "ValidationError"
    # we use this to handle errors from any other error handler classes
    exception_class = exception.__class__.__name__

    try:
        if response is not None or exception_class in handlers:
            response.data["status_code"] = response.status_code
            if "detail" in response.data:
                response.data["status"] = "error"
                response.data["message"] = response.data["detail"]
                del response.data["detail"]

            if "non_field_errors" in response.data:
                response.data["status"] = "fail"
                response.data["errors"] = response.data["non_field_errors"]
                del response.data["non_field_errors"]

            if "default_code" in response.data:
                response.data["code"] = response.data["default_code"]
                del response.data["default_code"]

            if isinstance(exception, Throttled):
                response.data["availableIn"] = exception.wait
                response.data["status"] = "error"
                response.data["message"] = response.data["detail"]

            # if exception has errors attribute, set errors field in response
            if hasattr(exception, "errors") and exception.errors:
                response.data["status"] = "error"
                response.data["errors"] = exception.errors
            else:
                # because some of these errors are returned as a dictionary, their
                # keys are none of the above, yet not of the type to be raised as a
                # TypeError exception
                response_data = {}
                response_data["status"] = "error"
                response_data["errors"] = response.data
                response.data = response_data
    except TypeError:
        # because some validation errors are returned by DRF as a list
        response_data = {}
        response_data["status"] = "fail"
        response_data["errors"] = response.data
        response.data = response_data
    return response
