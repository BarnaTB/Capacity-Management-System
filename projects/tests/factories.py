import factory
from django.utils import timezone

from projects.models import Project
from skills.tests.factories import CategoryFactory, SkillFactory


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=150)
    start_date = timezone.now().date()
    end_date = factory.LazyAttribute(lambda obj: obj.start_date + timezone.timedelta(days=30))

    @factory.post_generation
    def required_skills(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for skill in extracted:
                self.required_skills.add(skill)
        else:
            category = CategoryFactory.create()
            skill = SkillFactory.create(category=category)
            self.required_skills.add(skill)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in extracted:
                self.members.add(member)
