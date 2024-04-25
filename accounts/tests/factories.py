import factory

from accounts.models import DeveloperProfile, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = "test@amalitech.org"
    role = User.ADMIN
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "Password1")


class DeveloperProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeveloperProfile

    user = factory.SubFactory(UserFactory)
    availability = True

    @factory.post_generation
    def skills(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for skill in extracted:
                self.skills.add(skill)
