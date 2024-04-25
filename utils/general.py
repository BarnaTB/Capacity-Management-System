from datetime import datetime

from rest_framework import serializers

from django.core.files.storage import default_storage
from django.utils.text import slugify


def upload_to_s3(file):
    """Utility function to enable a user to upload files

    Args:
        file (_type_): the file to be uploaded

    Returns:
        str: URL of the saved photo from AWS
    """
    filename = slugify(file.name)
    try:
        path = default_storage.save(f"{filename}", file)
    except IOError:
        return None

    url = default_storage.url(path)

    return url

def get_date_from_string(date_string: str) -> datetime:
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise serializers.ValidationError("Invalid date format. Date should be in the format YYYY-MM-DD.")
