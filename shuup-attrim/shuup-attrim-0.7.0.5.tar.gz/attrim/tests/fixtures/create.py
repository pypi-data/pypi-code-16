from shuup.testing.factories import get_default_product_type

from attrim.interface import attrim
from attrim.models import Class
from attrim.types import AttrimType
from attrim.helpers import get_languages_list

from typing import List


def formset_post_data(
    cls_name: dict,
    cls_code: str,
    cls_type: AttrimType,
    option_forms: list,
) -> dict:
    output_post_data = {}

    # cls data
    output_post_data.update({'code': cls_code, 'type': cls_type})
    for lang_code, trans_name in cls_name.items():
        field_name = 'value_{lang_code}'.format(lang_code=lang_code)
        field_value = trans_name
        output_post_data.update({field_name: field_value})


    # formset management data
    initial_forms_count = 0
    for form in option_forms:
        is_new_form = form.get('is_new', False)
        if not is_new_form:
            initial_forms_count += 1
    output_post_data.update({
        'form-TOTAL_FORMS': len(option_forms),
        'form-INITIAL_FORMS': initial_forms_count,
        'form-MAX_NUM_FORMS': '',
    })

    # cls options formset data
    for form_number, form_dict in enumerate(option_forms):
        output_form = {}

        form_prefix = 'form-{number}-'.format(number=form_number)

        # order
        field_order_name = form_prefix + 'order'
        field_order_value = form_dict.get('order', '')
        output_form.update({field_order_name: field_order_value})

        # delete
        field_delete_name = form_prefix + 'DELETE'
        field_delete_value = form_dict.get('delete', '')
        output_form.update({field_delete_name: field_delete_value})

        # value
        if 'value' in form_dict:
            if type(form_dict['value']) is dict:
                values = form_dict['value']
                for field_name_short, field_value in values.items():
                    field_name = form_prefix + field_name_short
                    output_form.update({field_name: field_value})
            else:
                field_name = form_prefix + 'value'
                field_value = form_dict['value']
                output_form.update({field_name: field_value})

        if 'values' in form_dict:
            values = form_dict['values']
            for field_name_short, field_value in values.items():
                field_name = form_prefix + field_name_short
                output_form.update({field_name: field_value})


        output_post_data.update(output_form)

    return output_post_data


def option_forms(
    options: list,
    options_new: List[int] = [],
    options_delete: List[int] = [],
) -> list:
    option_forms = []
    for index, option in enumerate(options):
        option_form = {}

        option_form.update({'order': option['order']})

        if index in options_new:
            option_form.update({'is_new': True})
        if index in options_delete:
            option_form.update({'delete': True})

        option_field_trans_str_values = {}
        for lang_code in get_languages_list():
            input_name = 'value_{lang_code}'.format(lang_code=lang_code)
            input_value = option['values'][lang_code]
            option_field_trans_str_values.update({input_name: input_value})
        option_form.update({'values': option_field_trans_str_values})

        option_forms.append(option_form)

    return option_forms


def cls_trans_str(code: str, name: dict, options: list) -> Class:
    fake_class = attrim.cls.create(
        code=code,
        type=attrim.AttrimType.trans_str,
        name=name,
        product_type=get_default_product_type(),
    )
    fake_class.options = options
    return fake_class


def cls_int(code: str, name: dict, options: list) -> Class:
    int_cls = attrim.cls.create(
        code=code,
        type=attrim.AttrimType.int,
        name=name,
        product_type=get_default_product_type(),
    )
    int_cls.options = options
    return int_cls
