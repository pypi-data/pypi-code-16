from django import forms
from django.forms import BaseFormSet
from django.forms.formsets import DEFAULT_MIN_NUM, DEFAULT_MAX_NUM

from typing import List
from typing import Union

from shuup.admin.form_part import TemplatedFormDef
from shuup.admin.form_part import FormPart

from attrim.interface.attrim import cls


class AttributesForm(forms.Form):
    cls = forms.SlugField(widget=forms.HiddenInput)

    name = ''
    product = None
    form_cls = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.product = self.initial['product']

        cls_code = self.initial['cls']
        self.form_cls = cls.get(code=cls_code)

        self.name = self._get_form_name()

        self._declare_options_field()

    def save(self):
        cls_code = self.form_cls.code

        if self.product.attrims.is_exist(code=cls_code):
            attr = self.product.attrims.get(code=cls_code)
            new_attr_options = self.cleaned_data['options']
            attr.options = new_attr_options
        else:
            self.product.attrims.create(
                cls_code=cls_code,
                options=self.cleaned_data['options'],
            )

    def _declare_options_field(self):
        """
        Add field `options = MultipleChoiceField()` with choices for it from 
        `self.form_cls.options`.
        """
        # MultipleChoiceField require list of tuples, but attrim interface
        # returns just a list of options, so we need to convert the options
        # to tuples.
        options_choices = []
        for option in self.form_cls.options:
            options_choices.append(
                (option, option)
            )
        self.fields['options'] = forms.MultipleChoiceField(
            choices=options_choices,
            required=False,
            initial=self._get_initial_options(),
            # label for `options` is meaningless in form render
            label='',
        )

    def _get_form_name(self) -> str:
        return self.form_cls.code

    def _get_initial_options(self) -> Union[List, None]:
        """
        If class already exist, then return it's options like initial data for
        the form. Else return None.
        """
        initial_options = None
        
        if self.product.attrims.is_exist(code=self.form_cls.code):
            attr = self.product.attrims.get(code=self.form_cls.code)
            initial_options = attr.options

        return initial_options


class AttributeFormSet(BaseFormSet):
    validate_min = False
    min_num = DEFAULT_MIN_NUM
    validate_max = False
    max_num = DEFAULT_MAX_NUM
    absolute_max = DEFAULT_MAX_NUM
    can_delete = False
    can_order = False
    extra = 0
    form = AttributesForm
    #: AFAIK, it's required by shuup
    form_class = AttributesForm

    def __init__(self, *args, **kwargs):
        # add product to initial forms data, form will need the product for 
        # work with attrim
        for form_initial_dict in kwargs['initial']:
            form_initial_dict.update({'product': kwargs['product']})

        # we should pop this values, because super `__init__()` can't take them
        kwargs.pop('empty_permitted')
        kwargs.pop('request')
        kwargs.pop('prefix')
        kwargs.pop('files')
        kwargs.pop('product')
        super().__init__(*args, **kwargs)


class AttributesFormPart(FormPart):
    priority = 0
    name = 'attrim'
    formset = AttributeFormSet

    def get_form_defs(self) -> Union[TemplatedFormDef, None]:
        yield TemplatedFormDef(
            name=self.name,
            form_class=self.formset,
            template_name='attrim/admin/product/attrim.jinja',
            required=False,
            kwargs={
                'product': self.object,
                'request': self.request,
                'initial': self._get_formset_initial_data(),
            }
        )

    def form_valid(self, product_form):
        if self.name in product_form.forms:
            formset = product_form.forms[self.name]
            for form in formset:
                if form.has_changed():
                    form.save()

    def _get_formset_initial_data(self) -> list:
        formset_initial_data_list = []

        if not self._is_product_saved():
            return formset_initial_data_list

        if self._is_product_has_type():
            product_type = self.object.type
            for attr_cls in product_type.attrim_classes.all():
                form_initial_data = {'cls': attr_cls.code}
                formset_initial_data_list.append(form_initial_data)
        return formset_initial_data_list

    def _is_product_saved(self) -> bool:
        if self.object.pk is None:
            return False
        else:
            return True

    def _is_product_has_type(self) -> bool:
        if self.object.type:
            return True
        else:
            return False
