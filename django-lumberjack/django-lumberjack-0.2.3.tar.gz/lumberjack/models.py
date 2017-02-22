from django.db import models
from django.utils.encoding import python_2_unicode_compatible


class LogEntry(models.Model):
    level       = models.CharField(max_length=16)
    message     = models.TextField()
    logged_at   = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'lumberjack'


@python_2_unicode_compatible
class LogTag(models.Model):
    tag         = models.CharField(max_length=64)
    log_entries = models.ManyToManyField(LogEntry, related_name='tags')
    
    class Meta:
        app_label = 'lumberjack'

    def __str__(self):
        return self.tag
