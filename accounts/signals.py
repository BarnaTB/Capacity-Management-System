from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import DeveloperProfile, User


@receiver(post_save, sender=User)
def create_developer_profile(sender, instance, created, **kwargs):
    """Signal function to create a developer if the user who has been created
    is a developer

    Args:
        sender (User): model that's being listened to for the signal
        instance (User): the user whose profile is supposed to be created
        created (bool): checks if the user was created or not
    """
    if created and instance.role == User.DEVELOPER:
        DeveloperProfile.objects.get_or_create(user=instance)
