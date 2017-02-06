from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, PermissionsMixin, AbstractBaseUser
)
from django.contrib.auth.models import Group as BaseGroup
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class CUserManager(BaseUserManager):
    """A concrete Manager for concrete Users."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Set defaults and then use private method to create user."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Set defaults then use private method to create superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class AbstractCUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class User model with admin-compliant permissions.

    Email and password are required. Other fields are optional.
    """

    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': "A user with that email address already exists.",
        },
    )
    full_name = models.CharField(_('full name'), max_length=60, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        """Provide extra info to Django models system."""

        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def get_full_name(self):
        """Return the full_name."""
        return self.full_name

    def get_short_name(self):
        """Return the full_name for the user (same as get_full_name)."""
        return self.full_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class CUser(AbstractCUser):
    """
    User model for Django authentication system.

    Password and email are required. Other fields are optional.
    """

    class Meta(AbstractCUser.Meta):
        """Provide extra info to Django models system."""

        swappable = 'AUTH_USER_MODEL'


class Group(BaseGroup):
    """Group model for Django authentication system."""

    class Meta:
        """Provide extra info to Django models system."""

        proxy = True
