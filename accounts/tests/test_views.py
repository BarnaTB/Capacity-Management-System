from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient, force_authenticate

from accounts.tests.factories import User, UserFactory
from accounts.views import UserConfigView
from utils.auth import TokenGenerator


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("accounts:login")
        self.user = UserFactory.create(email="test@amalitech.com", is_active=True)
        self.payload = {"email": self.user.email, "password": "Password1"}

    def test_registered_user_can_login_successfully(self):
        """Test that a registered user can login successfully"""
        login_response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        self.assertContains(login_response, "access")
        self.assertContains(login_response, "refresh")
        self.assertIsInstance(login_response.data.get("access"), str)
        self.assertIsInstance(login_response.data.get("refresh"), str)

    def test_registered_user_cannot_login_with_wrong_credentials(self):
        """Test that a registered user cannot login with wrong credentials"""
        payload = {"email": self.user.email, "password": "password"}
        login_response = self.client.post(self.url, payload, format="json")

        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)


class AcceptInviteTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create(
            email="test@amalitech.com",
        )
        self.user.save()

        token_generator = TokenGenerator()
        token = token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        self.url = reverse(
            "accounts:user-retrieve-update", kwargs={"uid": uid, "token": token}
        )
        self.payload = {
            "email": self.user.email,
            "first_name": "John",
            "last_name": "Doe",
            "password": "Password1!",
        }

    def test_update_user_with_new_password_and_activation(self):
        """Test that an invited user can accept an invite successfully"""
        update_response = self.client.patch(self.url, self.payload, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.payload["email"])
        self.assertEqual(self.user.first_name, self.payload.get("first_name"))
        self.assertEqual(self.user.last_name, self.payload.get("last_name"))
        self.assertTrue(self.user.check_password(self.payload.get("password")))
        self.assertTrue(self.user.is_active)


class UserConfigTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.client = APIClient()
        cls.factory = RequestFactory()
        cls.user = UserFactory.create(
            email="test@amalitech.com",
        )
        cls.url = reverse("accounts:user")
        cls.view = UserConfigView.as_view()

    def test_return_user_config_successfully(self):
        """Test that the currently logged in user can retrieve their user details"""
        access_token = self.user.tokens.get("access")

        request = self.factory.get(self.url, format="json")
        force_authenticate(request, user=self.user, token=access_token)

        response = self.view(request)

        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data.get("email"), self.user.email)


class UserListViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = UserFactory.create()
        cls.project_manager_user = UserFactory.create(email="manager@amalitech.org", role=User.PROJECT_MANAGER)
        cls.developer_user = UserFactory.create(email="dev@amalitech.org", role=User.DEVELOPER)

        cls.url = reverse("accounts:user-list")

    def setUp(self) -> None:
        self.client = APIClient()

    def authenticate_user(self, user):
        """Method to authenticate user across test cases

        Args:
            user (User): User object to be authenticated and added to the
            client credentials
        """
        access_token = user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_admin_user_can_view_all_users(self):
        """Test that an ADMIN user can view a list of all users
        """
        self.authenticate_user(self.admin_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_project_manager_user_can_view_project_manager_and_developer_users(self):
        """Test that an PROJECT MANAGER user can view a list of all users
        except ADMIN users
        """
        self.authenticate_user(self.project_manager_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_developer_user_cannot_view_emplyees(self):
        """Test that an DEVELOPER user cannot view any employees
        """
        self.authenticate_user(self.developer_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeveloperProfileTestMixin:
    @classmethod
    def setUpTestData(cls) -> None:
        cls.developer_user = UserFactory.create(role=User.DEVELOPER)
        cls.payload = {
            "work_experience": [
                {
                    "job_title": "Software Developer",
                    "company_name": "Meta",
                    "skills_used": ["Python", "Django", "JavaScript"],
                    "start_date": "2022-01-03",
                    "end_date": "2023-05-11"
                },
                {
                    "job_title": "Software Developer",
                    "company_name": "Google",
                    "skills_used": ["Python", "Django", "JavaScript"],
                    "start_date": "2019-01-04",
                    "end_date": "2022-12-12"
                }
            ],
            "education": [
                {
                    "school_name": "University of Cape Town",
                    "program": "BSc. Computer Science",
                    "start_date": "2017-09-05",
                    "end_date": "2021-05-12"
                }
            ],
            "employment_status": "EMPLOYEE",
            "job_information": "Junior Associate",
        }

    def authenticate_user(self):
        """Method to authenticate user across test cases
        """
        access_token = self.developer_user.tokens.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")


class DeveloperProfileUpdateViewTestCase(DeveloperProfileTestMixin, TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("accounts:developer-profile-update")
        self.authenticate_user()

    def test_developer_update_profile_successfully(self):
        """Test that a user can update their profile successfully with their work experience and education background
        """
        response = self.client.patch(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("work_experience")), len(self.payload.get("work_experience")))
        self.assertEqual(len(response.data.get("education")), len(self.payload.get("education")))
        self.assertEqual(response.data.get("job_information"), self.payload.get("job_information"))
        self.assertEqual(response.data.get("employment_status"), self.payload.get("employment_status"))


class DeveloperProfileViewTestCase(DeveloperProfileTestMixin, TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("accounts:developer-profile")
        self.authenticate_user()

    def test_retrieve_developer_profile(self):
        """Test that a logged-in user can view their developer profile
        """
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), self.developer_user.developer_profile.first().pk)
        self.assertEqual(response.data.get("user").get("id"), self.developer_user.pk)
        self.assertIsInstance(response.data.get("education"), list)
        self.assertIsInstance(response.data.get("work_experience"), list)
