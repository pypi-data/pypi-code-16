import re
from string import Template

from django.forms.widgets import Widget
from django.http import QueryDict

from typing import Union

from attrim.models import Class
from attrim.types import OptionValue
from attrim.types import TransStr
from attrim.helpers import get_languages_list


class OptionValuesWidget(Widget):
    """
    Renders Form options.
    
    Parse Form options to str. Or, if it is trans_str type, then it will
    parse several field (like `value_en`, `value_fi`, ...) to a dict
    (see `get_trans_str_dict_from_post` method).
    """
    cls = None
    input_template = Template("""
        <input readonly
               type="${type}"
               name="${name}"
               value="${value}"
               step="${step}"
               ${hidden}
        >
    """)

    def __init__(self, cls: Class = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cls = cls

    # noinspection PyMethodOverriding
    def render(self, name: str, value: OptionValue, attrs: dict) -> str:
        field_name = name
        field_value = value
        
        if self.cls.is_int_type():
            return self._render_integer_input(field_name, field_value)
        
        elif self.cls.is_float_type():
            return self._render_float_input(field_name, field_value)
        
        elif self.cls.is_str_type():
            return self._render_text_input(field_name, field_value)
        
        elif self.cls.is_trans_str_type():
            return self._render_trans_str_input(field_name, field_value)

    def value_from_datadict(
        self,
        data: QueryDict,
        files: dict,
        name: str,
    ) -> Union[dict, str]:
        """
        Get field value from POST `data` by field `name`.
        Called once for a field, but may be called twice during one request.
        """
        if self.cls.is_trans_str_type():
            trans_str_dict = self._get_trans_str_dict_from_post(
                post_data=data,
                field_name_full=name,
            )
            return trans_str_dict
        else:
            field_value_raw = data[name]
            return field_value_raw

    def _render_integer_input(
        self,
        field_name: str,
        field_value: OptionValue,
    ) -> str:
        return self.input_template.safe_substitute(
            type='number',
            name=field_name,
            value=field_value,
            step='1',
        )

    def _render_float_input(
        self,
        field_name: str,
        field_value: OptionValue,
    ) -> str:
        return self.input_template.safe_substitute(
            type='number',
            name=field_name,
            value=field_value,
            step='any',
        )

    def _render_text_input(
        self,
        field_name: str,
        field_value: OptionValue,
    ) -> str:
        return self.input_template.safe_substitute(
            type='text',
            name=field_name,
            value=field_value,
        )

    def _render_trans_str_input(
        self,
        field_name: str,
        field_value: TransStr,
    ) -> str:
        """
        Compose html output from text inputs and language_switch (the switch
        for client-side logic).
        You may say that this is sort of a "reverse" version of the
        `get_trans_str_dict_from_post` method.
        
        Input:
            field_name: form-0-value
            field_value: {'en': 'swedish', 'fi': 'ruotsalainen'}
        Output:
            <input required
                   hidden
                   disabled
                   type="text"
                   step=""
                   name="form-0-value_en"
                   value="swedish"
            >
            <input hidden
                   disabled
                   type="text"
                   step=""
                   name="form-0-value_fi"
                   value="ruotsalainen"
            >
        """
        output = ''

        for lang_code, input_value in field_value.items():
            input = self.input_template.safe_substitute(
                type='text',
                name='{field_name}_{lang_code}'.format(
                    field_name=field_name,
                    lang_code=lang_code
                ),
                value=input_value,
                hidden='hidden',
            )
            output += input
        
        return output

    def _get_trans_str_dict_from_post(
        self,
        post_data: QueryDict,
        field_name_full: str
    ) -> dict:
        """
        Input example:
            post_data = {
                'form-0-value_en': 'swedish',
                'form-0-value_fi': 'ruotsalainen',
                'form-0-value_fr': 'suédois',
            }
            field_name_full = 'form-0-value'
        Output:
            {'en': 'swedish', 'fi': 'ruotsalainen', 'fr': 'suédois'}
        """
        trans_str_dict = {}

        form_number_match = re.match(
            r'form-(?P<form_number>[0-9])',
            field_name_full,
        )
        form_number = form_number_match.group('form_number')

        for lang_code in get_languages_list():
            field_name = 'form-{form_number}-value_{lang_code}'.format(
                form_number=form_number,
                lang_code=lang_code,
            )
            field_value = post_data.get(field_name, '')
            trans_str_dict.update({lang_code: field_value})
        
        return trans_str_dict
