from django.db import models
from django.contrib.auth.models import User

from . import validators


class Device(models.Model):
    MAC = models.CharField(
        primary_key=True,
        max_length=17,
        validators=[validators.validate_mac]
    )
    name = models.CharField(max_length=64)
    hostname = models.CharField(max_length=64,
                                validators=[validators.validate_hostname])

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.owner) + ": " + self.name
