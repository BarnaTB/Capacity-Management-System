
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from acms.settings_utils import get_env_variable
from utils.exceptions import CustomAPIException


def send_email(subject, message, email):
    try:
        from_email = f'Amalitech<{get_env_variable("EMAIL_HOST_USER")}>'
        mail = EmailMessage(subject, message, from_email, [email])
        mail.content_subtype = "html"
        mail.send()
        return True
    except Exception:
        return False


def send_project_assignment_email(developer, project):
    FRONTEND_DOMAIN_NAME = get_env_variable("FRONTEND_DOMAIN_NAME", "")
    FAIL_TO_SEND_MESSAGE = "Fail to send email!"

    project_link = f"{FRONTEND_DOMAIN_NAME}/{developer.user.id}/projects/"
    subject = "You have been assigned to a new project on ACMS"
    data = {
        "project_name": project.name,
        "project_link": project_link
    }
    message = render_to_string("notification_email.html", data)
    send = send_email(subject, message, developer.user.email)
    if not send:
        raise CustomAPIException(message=FAIL_TO_SEND_MESSAGE)
