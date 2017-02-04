from django.db import models

from cms.models import CMSPlugin
from cms.utils.compat.dj import python_2_unicode_compatible
from markdownx.models import MarkdownxField

@python_2_unicode_compatible
class MarkdownxPlugin(CMSPlugin):
    markdown_text = MarkdownxField()
    other_text = models.TextField()

    def __str__(self):
        text = self.markdown_text
        return (text[:50] + '...') if len(text) > 53 else text