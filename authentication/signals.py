from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


User = get_user_model()


@receiver(
    post_save,
    sender=User,
)
def ensure_profile(
    sender,
    instance,
    created,
    **kwargs,
):
    """
    Ensure every authenticated user has exactly one Profile.

    Existing users are also handled, so this remains safe if a
    user exists without a profile because of an older migration
    or manually created database record.
    """

    Profile.objects.get_or_create(
        user=instance,
    )