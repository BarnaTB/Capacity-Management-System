from storages.backends.s3boto3 import S3Boto3Storage

from acms.settings_utils import get_env_variable


class MediaStorage(S3Boto3Storage):
    """Storage backend to store all media files to directory called `media`
    in an S3 bucket

    Args:
        S3Boto3Storage (_type_): _description_
    """
    location = get_env_variable("AWS_S3_STORAGE_FOLDER", "dev")
    file_overwrite = False
