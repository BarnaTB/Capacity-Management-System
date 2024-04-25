from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from accounts.tests.factories import UserFactory
from skills.tests.factories import (CategoryFactory, SkillFactory,
                                    SkillRatingFactory)


class ListCreateCategoryAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.url = reverse("skills:list-create-categories")
        self.payload = {"name": "Frontend"}
        self.user = UserFactory.build()
        self.user.set_password("Password1!")
        self.user.save()

    def test_create_category_successfully(self):
        """Test that a category can be created successfully by ADMIN user"""
        access_token = self.user.tokens.get("access")
        category_slug = slugify(self.payload.get("name"))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("name"), self.payload.get("name"))
        self.assertEqual(response.data.get("slug"), category_slug)

    def test_list_categories_successfully(self):
        """Test that categories can be listed successfully by ADMIN user"""
        self.category = CategoryFactory.create()
        access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0].get("name"), self.category.name)
        self.assertEqual(response.data[0].get("slug"), self.category.slug)


class ListCreateSkillAPITestCase(TestCase):
    def setUp(self):
        self.category = CategoryFactory.create()
        self.client = APIClient()

        self.user = UserFactory.build()
        self.user.set_password("Password1!")
        self.user.save()

        self.url = reverse("skills:list-create-skills")
        self.payload = [{"name": "Python Django", "slug": self.category.slug}]
        self.access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_skill_successfully(self):
        """Test that a skill can be created successfully by an ADMIN user"""
        skill_slug = slugify(self.payload[0].get("name"))
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0].get("name"), self.payload[0].get("name"))
        self.assertEqual(response.data[0].get("slug"), skill_slug)
        self.assertIsInstance(response.data[0].get("category"), dict)
        self.assertEqual(
            response.data[0].get("category").get("name"), self.category.name
        )

    def test_create_batch_of_skills_successfully(self):
        """Test that a batch of skills can be created successfully by an ADMIN user"""
        self.payload = [
            {"name": "Python Django", "slug": self.category.slug},
            {"name": "Python Flask", "slug": self.category.slug},
            {"name": "Python FastAPI", "slug": self.category.slug},
        ]
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0].get("name"), self.payload[0].get("name"))
        self.assertEqual(response.data[1].get("name"), self.payload[1].get("name"))
        self.assertEqual(response.data[2].get("name"), self.payload[2].get("name"))

    def test_list_skills_successfully(self):
        """Test that skills can be listed successfully by all users"""
        skill = SkillFactory.create(category=self.category)
        response = self.client.get(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0].get("name"), skill.name)
        self.assertEqual(response.data[0].get("slug"), skill.slug)
        self.assertIsInstance(response.data[0].get("category"), dict)
        self.assertEqual(
            response.data[0].get("category").get("name"),
            self.category.name,
        )
        self.assertEqual(
            response.data[0].get("category").get("slug"),
            self.category.slug,
        )


class CategoryAPITestMixin:
    def setUp(self):
        self.client = APIClient()
        self.category = CategoryFactory.create()

        self.user = UserFactory.build()
        self.user.set_password("Password1!")
        self.user.save()

        self.access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.url = reverse(
            "skills:retrieve-update-delete-category", kwargs={"pk": self.category.pk}
        )


class CategoryRetrieveTestCase(CategoryAPITestMixin, TestCase):
    def test_retrieve_category_successfully(self):
        """Test that one category can be retrieved successfully"""
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("slug"), self.category.slug)
        self.assertEqual(response.data.get("name"), self.category.name)


class CategoryUpdateTestCase(CategoryAPITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.payload = {"name": "Frontend"}

    def test_update_category_successfully(self):
        """Test that one category can be updated successfully"""
        response = self.client.patch(self.url, self.payload, format="json")

        self.category.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), self.payload.get("name"))


class CategoryDeleteTestCase(CategoryAPITestMixin, TestCase):
    def test_delete_category_successfully(self):
        """Test that one category can be deleted successfully"""
        response = self.client.delete(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SkillRatingAPITestMixin:
    def setUp(self):
        self.skill = SkillFactory.create()
        self.user = UserFactory.create(role=User.DEVELOPER)
        self.developer_profile = self.user.developer_profile.first()

        self.url = reverse("skills:skillrating-list")
        self.client = APIClient()
        self.access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")


class CreateSkillRatingAPITestCase(SkillRatingAPITestMixin, TestCase):
    def test_create_skill_rating(self):
        """Test that a developer can add a skill rating to their profile
        successfully
        """
        payload = {"skill": self.skill.pk, "rating": 4.5, "comment": "Great skill!"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get("developer_profile"), self.developer_profile.id
        )
        self.assertEqual(response.data.get("skill"), payload.get("skill"))
        self.assertEqual(response.data.get("rating"), str(payload.get("rating")))
        self.assertEqual(response.data.get("comment"), payload.get("comment"))


class ListSkillRatingsAPITestCase(SkillRatingAPITestMixin, TestCase):
    def test_list_skill_ratings(self):
        """Test that a developer can get a list of their skill rating to their profile
        successfully
        """
        skill_rating = SkillRatingFactory.create(skill=self.skill, developer_profile=self.developer_profile)
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0].get("developer_profile"), self.developer_profile.pk)
        self.assertEqual(response.data[0].get("rating"), str(skill_rating.rating))
        self.assertEqual(response.data[0].get("comment"), skill_rating.comment)
        self.assertEqual(response.data[0].get("skill").get("name"), self.skill.name)
        self.assertEqual(response.data[0].get("skill").get("slug"), self.skill.slug)
