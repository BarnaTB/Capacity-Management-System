import datetime

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from accounts.models import DeveloperProfile, User
from core.models import TimestampMixin
from skills.models import Skill


class Project(TimestampMixin, models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=150)
    required_skills = models.ManyToManyField(Skill)
    start_date = models.DateField(_("Date"), default=datetime.date.today)
    end_date = models.DateField(_("Date"), default=datetime.date.today)
    slug = models.SlugField(primary_key=True)
    members = models.ManyToManyField(DeveloperProfile)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.required_skills}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
