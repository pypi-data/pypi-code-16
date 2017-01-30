from django.forms import ModelForm
from nimble.models.debt import Debt
from . fields import ToggledMarkdownxFormField
from . widgets import ToggleableMarkdownWidget


class DebtForm(ModelForm):
    description = ToggledMarkdownxFormField(
        widget=ToggleableMarkdownWidget, required=False
    )

    class Meta:
        model = Debt
        fields = ['title', 'description']
