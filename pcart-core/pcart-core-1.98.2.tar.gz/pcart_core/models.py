from django.db import models
from django.contrib.sites.models import Site
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
import uuid
import json


class ThemeSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.OneToOneField(Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='settings')

    data = JSONField(_('Data'), default=dict, blank=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Theme settings')
        verbose_name_plural = _('Theme settings')

    def __str__(self):
        return str(self.site)

    def get_upload_path(self, filename=None):
        from .utils import get_settings_upload_path
        return get_settings_upload_path(self.site_id, filename)

    def get_settings_fields(self):
        from django.core.files.storage import default_storage
        storage = default_storage
        result = json.loads(render_to_string('pcart/settings_schema.json'))

        _current = self.data.get('current', {})

        for group in result:
            for o in group.get('settings', []):
                if 'id' in o:
                    if o.get('type') in ['radio', 'select', 'text', 'collection', 'blog', 'link_list', 'color', 'textarea']:
                        o['value'] = _current.get(o['id'], o.get('default', ''))
                    elif o.get('type') in ['image']:
                        value = _current.get(o['id'], o.get('default', ''))
                        if value:
                            value = self.get_upload_path(value)
                            o['url'] = storage.url(value)
                        o['value'] = value
                    elif o.get('type') in ['checkbox']:
                        o['value'] = _current.get(o['id'], o.get('default', False))
        return result
