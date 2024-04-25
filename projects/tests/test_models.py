from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from projects.models import Project
from skills.tests.factories import SkillFactory


class ProjectTestCase(TestCase):
    def setUp(self) -> None:
        self.skill = SkillFactory.create()

    def test_project_create_project_successfully(self):
        """Test that the Project model can create a Project successfully
        """
        name = "Test Project"
        description = "Amazing project"
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=30)
        project = Project.objects.create(name=name, description=description, start_date=start_date, end_date=end_date)
        project.required_skills.add(self.skill)

        self.assertEqual(project.slug, slugify(name))
        self.assertEqual(project.name, name)
        self.assertEqual(project.description, description)
        self.assertEqual(project.pk, slugify(name))
        self.assertEqual(project.required_skills.all().first().pk, self.skill.pk)
