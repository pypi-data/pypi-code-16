from django.db import models

from joda_core.documents.models import Document


class MiscType(models.Model):
    DEFAULT_PK = 1
    name = models.CharField(max_length=255, unique=True, db_index=True)

    class JSONAPIMeta:
        resource_name = 'misc-types'

    def __str__(self):
        if self.pk == self.DEFAULT_PK:
            return self.name + ' (default, can not be deleted)'
        return self.name


class MiscDocument(Document):
    misc_type = models.ForeignKey(MiscType, blank=False, default=MiscType.DEFAULT_PK)

    class JSONAPIMeta:
        resource_name = 'misc-documents'
