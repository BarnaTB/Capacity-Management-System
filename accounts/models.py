from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.managers import CustomUserManager
from core.models import TimestampMixin


class User(TimestampMixin, AbstractUser):
    """
    Model class that extends the default User model and customizes
    some default field rules
    """

    ADMIN = "ADMIN"
    PROJECT_MANAGER = "PROJECT MANAGER"
    DEVELOPER = "DEVELOPER"
    ROLE_CHOICES = [
        (ADMIN, _("ADMIN")),
        (PROJECT_MANAGER, _("PROJECT MANAGER")),
        (DEVELOPER, _("DEVELOPER")),
    ]

    username = None
    email = models.EmailField(_("email_address"), unique=True)
    role = models.CharField(choices=ROLE_CHOICES, default=DEVELOPER, max_length=20)
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_("Shows whether or not this user has accepted their invite."),
    )
    profile_photo = models.URLField(blank=True)
    country = CountryField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self) -> str:
        return f"{self.email} - {self.role}"

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def get_users_by_role(self):
        """Method to filter users based on the currently logged in user

        Returns:
            Queryset: A queryset of User objects
        """
        role_query = {
            User.ADMIN: User.objects.all(),
            User.PROJECT_MANAGER: User.objects.filter(models.Q(role=User.PROJECT_MANAGER) | models.Q(role=User.DEVELOPER)),
        }

        return role_query.get(self.role, User.objects.none())


class DeveloperProfile(TimestampMixin, models.Model):
    """Model class for the Developer Profile

    Args:
        TimestampMixin (Model): an Abstract model that adds the create_date
        and last modfied date fields
        models (Model): base Django Model class
    """
    INTERN = "INTERN"
    EMPLOYEE = "EMPLOYEE"
    NATIONAL_SERVICE_PERSONS = "NATIONAL SERVICE PERSONS"
    EMPLOYMENT_STATUS_CHOICES = [
        (INTERN, _("INTERN")),
        (EMPLOYEE, _("EMPLOYEE")),
        (NATIONAL_SERVICE_PERSONS, _("NATIONAL SERVICE PERSONS")),
    ]

    ASSOCIATE = "Associate"
    JUNIOR_ASSOCIATE = "Junior Associate"
    SENIOR_ASSOCIATE = "Senior Associate"
    EXPERT = "Expert"

    JOB_INFORMATION_CHOICES = [
        (ASSOCIATE, _("Associate")),
        (JUNIOR_ASSOCIATE, _("Junior Associate")),
        (SENIOR_ASSOCIATE, _("Senior Associate")),
        (EXPERT, _("Expert")),
    ]

    class Meta:
        indexes = [models.Index(fields=["availability"])]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="developer_profile"
    )
    skills = models.ManyToManyField("skills.Skill", through="skills.SkillRating")
    availability = models.BooleanField(default=True)
    occupied = JSONField(default=dict, blank=True)
    current_project_start_date = models.DateField(_("Date"), null=True, blank=True)
    current_project_end_date = models.DateField(_("Date"), null=True, blank=True)
    employment_status = models.CharField(max_length=30, default=INTERN, choices=EMPLOYMENT_STATUS_CHOICES)
    job_information = models.CharField(max_length=30, default=ASSOCIATE, choices=JOB_INFORMATION_CHOICES)
    current_project = models.CharField(max_length=128, verbose_name='current_project', blank=True)

    def __str__(self) -> str:
        return f"""{self.user.first_name} - Available: {self.availability}"""


class WorkExperience(TimestampMixin, models.Model):
    """Model class to enable a developer to add their work experience

    Args:
        TimestampMixin (Model): an Abstract model that adds the create_date
        and last modfied date fields
        models (Model): base Django Model class
    """
    developer_profile = models.ForeignKey(DeveloperProfile, on_delete=models.CASCADE, related_name="work_experience")
    job_title = models.CharField(max_length=255, null=False, blank=True)
    company_name = models.CharField(max_length=50, null=False, blank=True)
    skills_used = ArrayField(models.CharField(max_length=255), default=list)
    start_date = models.DateField(null=False, blank=True)
    end_date = models.DateField(null=False, blank=True)


class Education(TimestampMixin, models.Model):
    """Model class to enable a developer to add their education background

    Args:
        TimestampMixin (Model): an Abstract model that adds the create_date
        and last modfied date fields
        models (Model): base Django Model class
    """
    developer_profile = models.ForeignKey(DeveloperProfile, on_delete=models.CASCADE, related_name='education')
    school_name = models.CharField(max_length=255)
    program = models.CharField(max_length=255)
    start_date = models.DateField(null=False, blank=True)
    end_date = models.DateField(null=False, blank=True)
