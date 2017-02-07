from django.db import models
from django.db.models import Model
from django.utils.translation import ugettext_lazy as _

from shuup.core.models import ProductType as ShuupProductType

from enumfields import EnumIntegerField
from typing import Dict
from typing import List
from typing import TypeVar
from typing import Union
from parler.models import TranslatedFields
from parler.models import TranslatableModel
from parler.utils.context import switch_language
from shuup_dev_utils.settings import DEFAULT_LANG
from shuup_dev_utils.settings import LANG_LIST

from attrim.types import AttrimType
from attrim.types import OptionValue
from attrim.types import TypeMixin
from attrim.helpers import get_languages_list


Attribute = TypeVar('Attribute')
Option = TypeVar('Option')

OptionDict = Dict[
    # key, i.e. 'value', 'values', 'order',
    str,
    # value/values/order
    Union[
        # value for `int`, `float` or `str` types
        OptionValue,
        # values for `trans_str` type
        Dict[str, str],
        # value for the `order` key
        int,
    ]
]


class Class(TranslatableModel, TypeMixin):
    product_type = models.ForeignKey(
        ShuupProductType,
        related_name='attrim_classes',
        related_query_name='attrim_cls',
        null=True, blank=True,
    )
    code = models.SlugField(unique=True)

    type = EnumIntegerField(AttrimType)

    translations = TranslatedFields(
        name=models.CharField(max_length=64, verbose_name=_('name')),
    )
    
    class JSONAPIMeta:
        resource_name = 'attrim-classes'

    @property
    def options(self) -> 'ClassOptionsInterface':
        return ClassOptionsInterface(cls=self)

    @options.setter
    def options(self, options: List[OptionDict]):
        self.options.remove_all()
        self.options.add(options)

    def get_name_translations(self) -> dict:
        names = {}
        for lang_code in LANG_LIST:
            with switch_language(self, lang_code):
                names.update({lang_code: self.name})
        return names

    def get_initial_data_for_form(self) -> List[Dict[str, OptionValue]]:
        """
        Return list for `OptionFormSet` initial data.

        Every dict in the list contains formset_form fields for an OptionForm
        in the formset.
        - `trans_str` example:
              {'order': 1, 'value': {'en': 'swedish', 'fr': 'suédois'}}
        - `str` example:
              {'order': 1, 'value': 'some value}
        """
        option_formset = []

        for option_model in self.option_models.all():
            option_form = {}

            option_form.update({'order': option_model.order})

            if self.is_int_type():
                option_form.update({'value': int(option_model.number_value)})
            if self.is_float_type():
                option_form.update({'value': float(option_model.number_value)})
            elif self.is_str_type():
                option_form.update({'value': option_model.str_value})
            elif self.is_trans_str_type():
                field_values = self._get_trans_str_values(option_model)
                option_form.update({'value': field_values})

            option_formset.append(option_form)
        
        return option_formset

    def _get_trans_str_values(self, option_model: Option) -> dict:
        """
        Output example:
            {'en': 'swedish', 'fr': 'suédois'}
        """
        fields_dict = {}

        for lang_code in get_languages_list():
            with switch_language(option_model, lang_code):
                field_value = option_model.trans_str_value
                fields_dict.update({lang_code: field_value})

        return fields_dict


class ClassOptionsInterface(list):
    cls = Class
    options = []

    def __init__(self, cls: Class):
        self.cls = cls
        self.options = self._get_options_list()
        super().__init__(self.options)

    def add(self, options: List[OptionDict] = None, option: OptionDict = None):
        if options is not None:
            # noinspection PyTypeChecker
            for option_data in options:
                self._add_option(option_data)
        elif option is not None:
            self._add_option(option)
        else:
            raise ValueError(
                'You must specify at least one of `add` arguments.'
            )

    def remove(self, option: OptionValue = None, options: List[OptionValue] = None):
        if option is not None:
            option_model = self.get_option_by_value(option)
            option_model.delete()
        elif options is not None:
            # noinspection PyTypeChecker
            for option_value in options:
                option_model = self.get_option_by_value(option_value)
                option_model.delete()
        else:
            raise ValueError(
                'You must specify at least one of `remove` arguments.'
            )

        self.options = self._get_options_list()

    def remove_all(self):
        """
        `self.option_models.clear()` will only remove `Value`s from a `Class`
        model, but will leave untouched `Attribute` model's `Value`s, so
        here should be explicit `delete()` call on every `Class` `Value`.
        """
        for option in self.cls.option_models.all():
            option.delete()

    def get_option_by_value(self, value: OptionValue) -> Model:
        """
        Can't use `Q` object because of `parler` API.
        """
        if self.cls.is_number_type():
            return self.cls.option_models.get(number_value=value)
        elif self.cls.is_str_type():
            return self.cls.option_models.get(str_value=value)
        elif self.cls.is_trans_str_type():
            if type(value) is dict:
                # then this is a whole trans text dict with lang key and values
                trans_str_value = value[DEFAULT_LANG]
            elif type(value) is str:
                trans_str_value = value
            else:
                raise ValueError('Wrong type of the value for lookup')

            option = self.cls.option_models.get(
                translations__trans_str_value=trans_str_value
            )
            return option
        else:
            raise ValueError('Option not found')

    def _add_option(self, option: OptionDict):
        """
        Create new `Option` for `self.cls`.
        """
        option_model = self.cls.option_models.create()

        option_model.order = option.get('order')

        if self.cls.is_number_type():
            option_model.number_value = option['value']

        elif self.cls.is_str_type():
            option_model.str_value = option['value']

        elif self.cls.is_trans_str_type():
            # examples of an `option` argument for trans str type:
            # {'order': 3, 'values': {'en': 'swedish', 'fr': 'suédois'}}
            # {'order': 3, 'value':  {'en': 'swedish', 'fr': 'suédois'}}
            if 'values' in option:
                values = option['values']
            elif 'value' in option:
                values = option['value']
            else:
                raise ValueError(
                    'Provided option dict does not have a `value[s]` key.'
                )

            for lang_key in values:
                with switch_language(option_model, lang_key):
                    str_value = values[lang_key]
                    option_model.trans_str_value = str_value

        option_model.save()

    def _get_options_list(self) -> List[OptionValue]:
        """
        Output example (str and trans_str will look indifferently):
            ['nod32', 'bitdefender', 'kaspersky']
        """
        options_list = []
        for option in self.cls.option_models.all():
            if self.cls.is_int_type():
                option_value_decimal = option.number_value
                options_list.append(int(option_value_decimal))
            elif self.cls.is_float_type():
                option_value_decimal = option.number_value
                options_list.append(float(option_value_decimal))
            elif self.cls.is_str_type():
                options_list.append(option.str_value)
            elif self.cls.is_trans_str_type():
                options_list.append(option.trans_str_value)
        return options_list
