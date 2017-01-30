from django.forms import ModelForm
from nimble.models.feature import Feature
from . fields import ToggledMarkdownxFormField
from . widgets import ToggleableMarkdownWidget


class FeatureForm(ModelForm):
    description = ToggledMarkdownxFormField(
        widget=ToggleableMarkdownWidget
    )

    class Meta:
        model = Feature
        fields = ['title', 'description']
