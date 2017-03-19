
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class UserProfile(models.Model):

    user = models.OneToOneField(User, related_name='profile')

    mobile = models.CharField(_('Mobile number'), max_length=255, blank=True)

    address = models.CharField(_('Address'), max_length=255, blank=True)
