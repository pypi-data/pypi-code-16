from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon='site')
class AnalyticsSettings(BaseSetting):
    google_analytics = models.CharField(
        max_length=64, blank=True, null=True,
        help_text='Your google analytics code')
