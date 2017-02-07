from django.forms import Field

from typing import Union

from attrim.models import Class
from attrim.types import OptionValue
from attrim.admin.cls.views.forms.widgets import OptionValuesWidget


class OptionField(Field):
    cls = None
    widget = None
    
    empty_values = ['']
    required = True
    label = None
    localize = False
    
    def __init__(self, cls: Class, *args, **kwargs):
        self.cls = cls
        self.widget = OptionValuesWidget(cls=self.cls)
        super().__init__(*args, **kwargs)

    def to_python(self, value: str) -> Union[OptionValue, None]:
        if value in self.empty_values:
            return None
        elif self.cls.is_int_type():
            return int(value)
        elif self.cls.is_float_type():
            return float(value)
        elif self.cls.is_str_type():
            return str(value)
        elif self.cls.is_trans_str_type():
            # value is already parsed by `OptionValuesWidget`
            return value
