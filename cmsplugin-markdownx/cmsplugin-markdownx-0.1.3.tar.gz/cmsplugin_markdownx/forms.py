from django.forms import ModelForm
from .models import MarkdownxPlugin

from markdownx.widgets import MarkdownxWidget

class MarkdownxPluginForm(ModelForm):
    class Meta:
        model = MarkdownxPlugin
        fields = ['markdown_text','other_text']
        widgets = {
            'markdown_text': MarkdownxWidget
        }
