from decimal import Decimal
from django.utils.translation import ugettext_lazy as _

from typing import Union
from typing import Dict
from enumfields import Enum


TransStrLangCode = str
TransStrValue = str
TransStr = Dict[TransStrLangCode, TransStrValue]
#: represents all valid data types for `Option` model
OptionValue = Union[
    int,
    float,
    Decimal,
    str,
    TransStr,
]


class AttrimType(Enum):
    int = 1
    float = 3

    trans_str = 20
    str = 21

    class Labels:
        # Translators: attrim type's labels
        int = _('integer')
        float = _('decimal')

        trans_str = _('translated string')
        str = _('string')


class TypeMixin:
    """
    It is quite ugly to write all the time something like:
        if (
            self.type == AttrimType.str or
            self.type == AttrimType.trans_str
        ):
    So this class to the rescue.
    """

    #: will be `Class.type` on an instance.
    type = None

    def is_int_type(self) -> bool:
        return self.type == AttrimType.int

    def is_float_type(self) -> bool:
        return self.type == AttrimType.float

    def is_str_type(self) -> bool:
        return self.type == AttrimType.str

    def is_trans_str_type(self) -> bool:
        return self.type == AttrimType.trans_str

    def is_number_type(self) -> bool:
        return self.is_int_type() or self.is_float_type()
