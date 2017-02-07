import decimal
from typing import List

from django.db.models import QuerySet

from attrim.models import Class
from attrim.types import OptionValue
from attrim.interface import cls as cls_interface


OptionValueRaw = str


def filter_product_qs_by(
    option_values_raw: List[OptionValueRaw],
    product_qs_source: QuerySet,
    cls: Class = None,
    cls_code: str = None,
) -> QuerySet:
    if not cls and not cls_code:
        raise ValueError('You must specify `cls` or `cls_code` argument.')
    
    cls_provided = cls or cls_interface.get(cls_code)
    option_values = _convert_option_values(cls_provided, option_values_raw)

    if cls_provided.is_number_type():
        product_qs_filtered = product_qs_source.filter(
            attrim__cls=cls_provided,
            attrim__option_model__number_value__in=option_values,
        )
    elif cls_provided.is_str_type():
        product_qs_filtered = product_qs_source.filter(
            attrim__cls=cls_provided,
            attrim__option_model__str_value__in=option_values,
        )
    elif cls_provided.is_trans_str_type():
        product_qs_filtered = product_qs_source.filter(
            attrim__cls=cls_provided,
            attrim__option_model__translations__trans_str_value__in=option_values,
        )
    else:
        product_qs_filtered = product_qs_source.filter(
            attrim__cls=cls_provided,
            attrim__option_model__translations__trans_str_value__in=option_values,
        )
    
    return product_qs_filtered


def _convert_option_values(cls: Class, option_values_raw: List[str]) -> List[OptionValue]:
    if cls.is_number_type():
        option_values = []
        for option_value_raw in option_values_raw:
            option_values.append(_convert_option_value(cls, option_value_raw))
        return option_values
    else:
        return option_values_raw


def _convert_option_value(cls: Class, option_value_raw: str) -> OptionValue:
    if cls.is_number_type():
        return decimal.Decimal(option_value_raw)
    else:
        return option_value_raw
