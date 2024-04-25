from collections import ChainMap
from functools import wraps

from utils.exceptions import CustomAPIException


def required_fields(parameters: list):
    """Decorator function to ensure that a request has
    the required parameters

    Args:
        parameters (list): A list of required request parameters
    """

    def validator(f):
        @wraps(f)
        def func_wrap(view, request, *args, **kwargs):
            if request:
                data = ChainMap(request.GET, request.data, kwargs)
                for parameter in parameters:
                    value = data.get(parameter)
                    if value is None:
                        message = parameter + " is required"
                        raise CustomAPIException(message=message)
            return f(view, request, *args, **kwargs)

        return func_wrap

    return validator
