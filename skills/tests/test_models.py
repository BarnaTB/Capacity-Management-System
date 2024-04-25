from django.test import TestCase
from django.utils.text import slugify

from skills.models import Category, Skill
from skills.tests.factories import CategoryFactory


class CategoryTests(TestCase):
    def test_create_category_successfully(self):
        """Test that the category model can create the user object"""
        name = "Frontend Engineer"
        slug = slugify(name)
        category = Category.objects.create(name=name)
        self.assertEqual(category.name, name)
        self.assertEqual(category.slug, slug)
        self.assertEqual(category.pk, slug)


class SkillModelTestCase(TestCase):
    def setUp(self) -> None:
        self.category = CategoryFactory.create()

    def test_create_category_successfully(self):
        """Test that the skill model can create the user object"""
        name = "Python Django"
        slug = slugify(name)
        skill = Skill.objects.create(name=name, category=self.category)
        self.assertEqual(skill.name, name)
        self.assertEqual(skill.slug, slug)
        self.assertEqual(skill.pk, slug)
