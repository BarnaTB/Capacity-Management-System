from django.db import models
from django.utils.text import slugify

from accounts.models import DeveloperProfile
from core.models import TimestampMixin


class Category(TimestampMixin, models.Model):
    slug = models.SlugField(primary_key=True)
    name = models.CharField(max_length=20, blank=False, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Skill(TimestampMixin, models.Model):
    slug = models.SlugField(primary_key=True)
    name = models.CharField(max_length=20, blank=False, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category"
    )

    def __str__(self) -> str:
        return f"{self.name} - {self.category.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SkillRating(TimestampMixin, models.Model):
    """Model class for the Developer Profile

    Args:
        TimestampMixin (Model): an Abstract model that adds the create_date
        and last modfied date fields
        models (Model): base Django Model class
    """

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    developer_profile = models.ForeignKey(DeveloperProfile, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"""
        {self.developer_profile.user.id} -
        {self.skill.name} - {self.rating}"""
