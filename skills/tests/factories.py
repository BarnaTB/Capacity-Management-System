import factory

from accounts.tests.factories import DeveloperProfileFactory
from skills.models import Category, Skill, SkillRating


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = "category name"
    slug = "category-name"


class SkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skill

    name = "Python Django"
    slug = "python-django"
    category = factory.SubFactory(CategoryFactory)


class SkillRatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SkillRating

    rating = 3.0
    comment = "Great skill!"
    skill = factory.SubFactory(SkillFactory)
    developer_profile = factory.SubFactory(DeveloperProfileFactory)
