from django import forms

from . widgets import ToggleableMarkdownWidget


class ToggledMarkdownxFormField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super(ToggledMarkdownxFormField, self).__init__(*args, **kwargs)
        # if not issubclass(self.widget.__class__, ToggleableMarkdownWidget):
        self.widget = ToggleableMarkdownWidget()
