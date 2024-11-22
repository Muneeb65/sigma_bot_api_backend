from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.managers import CustomUserManager


class User(AbstractUser):
    """
    Custom User model
    """

    class UserType(models.IntegerChoices):
        pass

    email = models.EmailField(_('email address'), unique=True)
    user_type = models.PositiveSmallIntegerField(choices=UserType.choices, null=True, blank=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.email
