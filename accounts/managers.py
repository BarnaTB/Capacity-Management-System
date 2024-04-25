from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from utils.validations import validate_email, validate_password


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        validate_email(email)
        if password:
            validate_password(password)
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("A superuser must also be staff"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("A superuser must have the superuser"))
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)

    def get(self, **kwargs):
        return self.get_queryset().get(**kwargs)
