import logging
import re

from rest_framework.serializers import ValidationError

from acms.settings_utils import get_env_variable
from utils.exceptions import CustomAPIException

logger = logging.getLogger(__name__)


def validate_password(password: str):
    """Validator function to validate that the user's password
    follows the set rules/criteria

    Args:
        password (str): the password that the user intends to use

    Raises:
        ValidationError: an error message thrown if the user's intended
        password does not follow the set rules
    """
    error = (
        "Ensure your password is at least 8 characters long, "
        "has an uppercase, lowercase, a numerical character and no leading or "
        "character and no leading or trailing spaces."
    )
    regex = r"(?P<password>((?=\S*[A-Z])(?=\S*[a-z])(?=\S*\d)\S))"

    if re.compile(regex).search(password) is None:
        raise ValidationError(error)


def validate_email(email: str):
    """Validator function to validate that the email follows set rules
    e.g belongs to the a given set of allowed domains

    Args:
        email (str): a string containing the email address

    Raises:
        ValidationError: an error message thrown if the user's intended
        email does not follow the set criteria
    """
    error = "Email address does not belong to the AmaliTech organization"
    allowed_domains = get_env_variable("ALLOWED_EMAIL_DOMAINS")
    domain_name_index = email.find("@")
    email_domain = email[domain_name_index:]

    if email_domain not in allowed_domains:
        raise CustomAPIException(message=error)
