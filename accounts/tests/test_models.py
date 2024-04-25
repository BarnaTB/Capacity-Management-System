from django.contrib.auth import get_user_model
from django.test import TestCase


class UserManagerTests(TestCase):
    def test_create_user(self):
        """Test that the user model can create the user object"""
        User = get_user_model()
        email = "bar@amalitech.com"
        user = User.objects.create_user(email=email, password="Password1")
        self.assertEqual(user.email, email)
        self.assertEqual(user.role, User.DEVELOPER)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.username)

        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")
