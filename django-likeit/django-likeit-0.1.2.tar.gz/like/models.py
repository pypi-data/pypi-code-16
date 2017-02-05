from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .managers import LikeManager


class Like(models.Model):
    """
    """

    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'))
    target_content_type = models.ForeignKey(ContentType)
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_content_type', 'target_object_id')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = LikeManager()

    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "timestamp"
        unique_together = ("user", "target_content_type", "target_object_id")
        verbose_name = _("like")
        verbose_name_plural = _("likes")

    def __unicode__(self):
        return u"{} liked {}".format(self.user, self.target)
