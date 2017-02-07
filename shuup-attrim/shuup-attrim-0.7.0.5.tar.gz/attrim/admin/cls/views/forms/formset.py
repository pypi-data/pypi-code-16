from django import forms
from django.forms import Form
from django.forms import BaseFormSet
from django.forms.formsets import DEFAULT_MIN_NUM
from django.forms.formsets import DEFAULT_MAX_NUM
from django.utils.functional import cached_property

from typing import List

from attrim.admin.cls.views.forms.fields import OptionField
from attrim.models import Class


class OptionForm(Form):
    cls = None
    
    order = forms.IntegerField(
        widget=forms.NumberInput(attrs={'readonly': 'readonly'}),
        required=False,
    )
    
    def __init__(self, cls: Class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cls = cls
        self.fields['value'] = OptionField(cls=self.cls)

    def delete(self):
        option_value = self.cleaned_data['value']
        self.cls.options.remove(option=option_value)

    def create(self):
        self.cls.options.add(option=self.cleaned_data)


class OptionFormSet(BaseFormSet):
    cls = None
    options = []

    form = OptionForm
    can_delete = True
    #: I use a custom `order` field (see form above), because I need it to
    #: render itself like a read-only field.
    can_order = False
    #: Extra fields can be added only through client logic,
    #: because they are require specified by user `Class` `type`.
    extra = 0
    
    min_num = DEFAULT_MIN_NUM
    max_num = DEFAULT_MAX_NUM
    absolute_max = DEFAULT_MAX_NUM * 2
    validate_min = False
    validate_max = False
    
    def __init__(self, *args, **kwargs):
        self.cls = kwargs.pop('cls')
        super().__init__(*args, **kwargs)

    def save(self):
        for option_created in self.extra_forms:
            option_created.create()
        
        for option_deleted in self.deleted_forms:
            option_deleted.delete()

    @cached_property
    def forms(self) -> List[OptionForm]:
        """
        Overwrite default django `forms()` method for passing to every
        formset_form current `Class` instance, because it is required by
        `OptionField` and `OptionValuesWidget`.
        
        Instantiates forms at first property access.
        """
        formset_forms = []
        # DoS protection is included in total_form_count()
        for form_number in range(self.total_form_count()):
            form = self._construct_form(
                form_number,
                cls=self.cls,
            )
            formset_forms.append(form)
        return formset_forms
