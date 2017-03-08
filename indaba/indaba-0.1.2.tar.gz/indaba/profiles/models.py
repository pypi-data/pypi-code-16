from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User)
    bio = models.TextField(max_length=600)
    phone_number = models.CharField(max_length=16)
    home_page = models.CharField(max_length=255)
    twitter_handle = models.CharField(max_length=15)
    github_username = models.CharField(max_length=32)

    def __str__(self):
        return u'%s' % self.user
