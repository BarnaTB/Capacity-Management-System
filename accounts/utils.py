import logging

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from six import text_type

from accounts.models import User

logger = logging.getLogger(__name__)


def validate_user_by_uid(uid):
    """Validator function to validate users using an encoded user id

    Args:
        uid (str): an encoded string of the user id

    Returns:
        _type_: _description_
    """
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
        return user
    except User.DoesNotExist:
        return None
    except Exception as e:
        logger.exception(
            f"[RESET PASSWORD] Error while decoding uid.\n" f"Error: {text_type(e)}"
        )
        return None
