from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from accounts.tests.factories import UserFactory
from projects.tests.factories import ProjectFactory
from skills.tests.factories import (CategoryFactory, SkillFactory,
                                    SkillRatingFactory)


class CreateProjectTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("projects:project-create")

    @classmethod
    def setUpTestData(cls) -> None:
        cls.category = CategoryFactory.create()
        cls.skill = SkillFactory.create(category=cls.category)
        cls.user = UserFactory.create()
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=30)
        cls.project_data = {
            "name": "Test Project",
            "description": "Project Description",
            "start_date": start_date,
            "end_date": end_date,
            "required_skills": [cls.skill.pk]
        }

    def test_create_project_successfully(self):
        """Test that an ADMIN or PROJECT MANAGER can create a project successfully
        """

        access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(self.url, self.project_data, format="json")

        project_slug = slugify(self.project_data.get("name"))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("slug"), project_slug)
        self.assertEqual(response.data.get("name"), self.project_data.get("name"))
        self.assertEqual(response.data.get("description"), self.project_data.get("description"))
        self.assertEqual(response.data.get("required_skills"), self.project_data.get("required_skills"))


class ProjectTestMixin:
    @classmethod
    def setUpTestData(cls) -> None:
        cls.project = ProjectFactory.create()
        cls.user = UserFactory.create()


class ListProjectsTestCase(ProjectTestMixin, TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("projects:project-list")

    def test_list_projects_successfully(self):
        """Test that projects can be listed successfully
        """
        access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data.get("results"), list)
        self.assertEqual(response.data["results"][0].get("slug"), self.project.slug)
        self.assertEqual(response.data["results"][0].get("name"), self.project.name)
        self.assertEqual(response.data["results"][0].get("description"), self.project.description)


class RetreiveProjectDetailViewTestCase(ProjectTestMixin, TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("projects:project-detail", kwargs={"slug": self.project.pk})

    def test_get_project_details_successfully(self):
        """Test that a project's details can be retrieved successfully
        """
        access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("slug"), self.project.slug)
        self.assertEqual(response.data.get("name"), self.project.name)
        self.assertEqual(response.data.get("description"), self.project.description)


class DestroyProjectTestCase(ProjectTestMixin, TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("projects:project-delete", kwargs={"slug": self.project.pk})

    def test_update_project_successfully(self):
        """Test that a project can be deleted successfully
        """
        access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AssignProjectToDeveloperTestCase(ProjectTestMixin, TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.developer = UserFactory.create(email="dev@amalitech.org", role=User.DEVELOPER)
        self.url = reverse("projects:project-assign-to-developer", kwargs={"slug": self.project.pk})

    def test_user_can_be_assigned_to_project_successfully(self):
        """Test that a user can be assigned to a project successfully
        """
        payload = {
            "members": [self.developer.developer_profile.first().pk]
        }
        access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SuggestedDevelopersListTestCase(ProjectTestMixin, TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("projects:suggested-developers-list", kwargs={"slug": self.project.pk})

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.skill = cls.project.required_skills.first()
        cls.developer = UserFactory.create(email="dev@amalitech.org", role=User.DEVELOPER)
        cls.developer_profile = cls.developer.developer_profile.first()
        cls.skill_rating = SkillRatingFactory.create(skill=cls.skill, developer_profile=cls.developer_profile)

    def test_suggest_developers_successfully(self):
        """Test that available developers can be suggested for a project successfully
        """
        access_token = self.user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertContains(response, "developer_profile")
        self.assertContains(response, "match_percentage")
        self.assertEqual(response.data[0].get("developer_profile").get("id"), self.developer_profile.pk)
        self.assertEqual(response.data[0].get("match_percentage"), 100.0)
