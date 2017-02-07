from django.db.models import QuerySet
from shuup.core.models import ProductType

from typing import Dict
from typing import Union
from typing import List
from parler.utils.context import switch_language

from attrim.models import Class
from attrim.types import OptionValue
from attrim.types import AttrimType


_type_func = type


# noinspection PyShadowingBuiltins,PyDefaultArgument
def create(
    code: str,
    type: AttrimType,
    name: Union[Dict[str, str], str] = '',
    product_type: ProductType = None,
    options: List[OptionValue] = [],
) -> Class:
    new_cls = Class(
        code=code,
        # `name` need to hand manually if it has translations, see below
        name='',
        type=type,
        product_type=product_type,
    )

    if _type_func(name) is dict:
        # set name for all languages
        for lang_code in name:
            with switch_language(new_cls, lang_code):
                new_cls.name = name[lang_code]
    else:
        new_cls.name = name

    new_cls.save()

    new_cls.options = options
    
    return new_cls


def delete(code: str = None, pk: int = None):
    if code is not None:
        Class.objects.get(code=code).delete()
    elif pk is not None:
        Class.objects.get(pk=pk).delete()
    else:
        raise ValueError('You must specify at least of the arguments.')


def get(code: str = None, pk: int = None) -> Class:
    if code is not None:
        return Class.objects.get(code=code)
    elif pk is not None:
        return Class.objects.get(pk=pk)
    else:
        raise ValueError('You must specify at least one of the arguments.')


def get_all() -> QuerySet:
    return Class.objects.all()
