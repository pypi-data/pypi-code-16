from django.db import models
from markitup.fields import MarkupField
from django.core.urlresolvers import reverse
from django.conf import settings


class Talk_Type(models.Model):

    talk_types = (
        ('S', "Short_Talk"),
        ('L', "Long_Talk"),
         ('T', "Tutorial"),
    )

    name = models.CharField(choices=talk_types, max_length=1)

    def __str__(self):
        return u"%s" % (self.name)


class Proposal(models.Model):

    # proposal = models.CharField(max_length=255, blank=False)
    title = models.CharField(max_length=1024)
    abstract = MarkupField(help_text="Describe what your talk is about")
    talk_type = models.ForeignKey(Talk_Type)
    proposal_id = models.AutoField(primary_key=True, default=None)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="proposals", default='')
    # meetup = models.ForeignKey()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("home")
