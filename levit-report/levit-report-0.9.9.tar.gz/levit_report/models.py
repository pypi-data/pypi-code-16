from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


CONVERT_CHOICES = [
    ('pdf', 'pdf'),
    ('doc', 'doc'),
    ('docx', 'docx'),
    ('xls', 'xls'),
    ('xlsx', 'xlsx'),
]

class Document(models.Model):

    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)
    source = models.FileField(_('source'), upload_to='reports')
    convert_to = models.CharField(_('convert to'), max_length=5, choices=CONVERT_CHOICES, blank=True, null=True)
    merge_with_tos = models.BooleanField(_('merge with tos'), default=False)
    content_type = models.ForeignKey(ContentType, related_name='reports', verbose_name=_('content type'))
    get_language_from_target = models.BooleanField(_('get language from target'), default=False)

    def __str__(self):
        return self.name
