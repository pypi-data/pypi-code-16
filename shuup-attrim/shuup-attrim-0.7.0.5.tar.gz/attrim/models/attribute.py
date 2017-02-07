from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model

from shuup.core.models import Product as ShuupProduct

from attrim.types import AttrimType
from attrim.types import TypeMixin
from attrim.types import OptionValue
from attrim.models.cls import Class

from typing import List


class AttrsManager(models.Manager, TypeMixin):
    #: details: https://docs.djangoproject.com/en/1.9/topics/db/managers/
    use_for_related_fields = True

    def create(
        self,
        product: ShuupProduct,
        options: List[OptionValue],
        cls_obj: Class = None,
        cls_code: str = None,
    ) -> 'Attribute':
        cls = cls_obj or Class.objects.get(code=cls_code)
        
        # noinspection PyUnresolvedReferences
        attribute = super().create(cls=cls, product=product, type=cls.type)

        for option_value in options:
            option_model = get_cls_option_by_value(cls, option_value)
            attribute.option_models.add(option_model)

        return attribute

    # noinspection PyUnresolvedReferences,PyUnusedLocal
    def get(
        self,
        code: str = None,
        cls: Class = None,
        *args, **kwargs
    ) -> 'Attribute':
        """
        Optional overwrite of `Manager.get` method.
        """
        if code is None:
            return super().get(*args, **kwargs)
        else:
            return super().get(cls__code=code, *args, **kwargs)

    # TODO: add possibility to delete attribute by it's class
    def delete(self, code: str):
        self.get(code=code).delete()

    # TODO: add possibility to call it with a `cls` in place of the `code`
    def is_exist(self, code: str) -> bool:
        try:
            # noinspection PyUnresolvedReferences
            super().get(cls__code=code)
            # TODO: don't catch
        except ObjectDoesNotExist:
            return False
        else:
            return True


class Attribute(models.Model, TypeMixin):
    product = models.ForeignKey(
        ShuupProduct,
        related_name='attrims',
        related_query_name='attrim',
        on_delete=models.CASCADE,
    )
    cls = models.ForeignKey(
        Class,
        related_name='attrim',
        on_delete=models.CASCADE,
    )

    objects = AttrsManager()

    class Meta:
        # `cls` contains the name the attribute, so you cannot have two attribute
        # values connected to the same name on one product
        unique_together = ('product', 'cls')

    @property
    def name(self) -> str:
        return self.cls.name

    @property
    def code(self) -> str:
        return self.cls.code

    @property
    def type(self) -> AttrimType:
        """
        `TypeMixin` expects to find `type` attribute on the model.
        """
        return self.cls.type

    @property
    def options(self) -> List[OptionValue]:
        options = []
        for option_model in self.option_models.all():
            if self.is_int_type():
                option_value_processed = int(option_model.number_value)
                options.append(option_value_processed)
            elif self.is_float_type():
                option_value_processed = float(option_model.number_value)
                options.append(option_value_processed)
            elif self.is_str_type():
                options.append(option_model.str_value)
            elif self.is_trans_str_type():
                options.append(option_model.trans_str_value)
            else:
                raise TypeError('Cannot determine attribute type')
        return options

    # TODO: input data check
    @options.setter
    def options(self, options: List[OptionValue]):
        """
        Input example: `['nod32', 'bitdefender', 'kaspersky']`
        """
        self.option_models.clear()

        for option_value in options:
            option_model = get_cls_option_by_value(self.cls, option_value)
            self.option_models.add(option_model)


def get_cls_option_by_value(cls: Class, value: OptionValue) -> Model:
    if cls.is_number_type():
        option_model = cls.option_models.get(number_value=value)
    elif cls.is_str_type():
        option_model = cls.option_models.get(str_value=value)
    elif cls.is_trans_str_type():
        option_model = cls.option_models.get(translations__trans_str_value=value)
    else:
        raise TypeError('Cannot determine cls type')

    return option_model
