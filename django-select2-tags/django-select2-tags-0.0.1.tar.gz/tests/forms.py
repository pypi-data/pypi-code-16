from select2_tags import forms

from tests import models as test_models


class MyFkForm(forms.Select2ModelForm):
    class Meta:
        model = test_models.MyNullableFkModel
        exclude = []

    my_fk_field = forms.Select2ModelChoiceField(
        'name', queryset=test_models.MyRelatedModel.objects.all(), required=False)


class MyM2mForm(forms.Select2ModelForm):
    class Meta:
        model = test_models.MyM2mModel
        exclude = []

    my_m2m_field = forms.Select2ModelMultipleChoiceField(
        'name', queryset=test_models.MyRelatedModel.objects.all(), required=False)
