from django.db import models
from django.contrib.contenttypes.models import ContentType


CONVERT_CHOICES = [
    ('pdf', 'pdf'),
    ('doc', 'doc'),
    ('docx', 'docx'),
    ('xls', 'xls'),
    ('xlsx', 'xlsx'),
]

class Document(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    source = models.FileField(upload_to='reports')
    convert_to = models.CharField(max_length=5, choices=CONVERT_CHOICES, blank=True, null=True)
    merge_with_tos = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, related_name='reports')

    def __str__(self):
        return self.name
