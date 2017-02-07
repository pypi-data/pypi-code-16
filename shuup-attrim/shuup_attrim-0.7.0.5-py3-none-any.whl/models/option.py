from typing import Union

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parler.models import TranslatedFields
from parler.models import TranslatableModel

from attrim.models.cls import Class
from attrim.models.attribute import Attribute


# TODO: cls and value must be unique together
class Option(TranslatableModel):
    attribute = models.ManyToManyField(
        Attribute,
        related_name='option_models',
        related_query_name='option_model',
        blank=True,
    )
    cls = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='option_models',
        related_query_name='option_model',
        null=True, blank=True,
    )
    order = models.PositiveSmallIntegerField(null=True, blank=True)

    number_value = models.DecimalField(
        max_digits=36,
        decimal_places=9,
        verbose_name=_('numeric value'),
        null=True, blank=True,
    )
    str_value = models.TextField(blank=True)
    translations = TranslatedFields(
        trans_str_value=models.TextField(blank=True)
    )

    class Meta:
        ordering = ['order']
        # unique_together = ('product', 'cls')

    @property
    def value(self) -> Union[int, float, str]:
        if self.cls.is_int_type():
            return int(self.number_value)
        elif self.cls.is_float_type():
            return float(self.number_value)
        elif self.cls.is_str_type():
            return str(self.str_value)
        elif self.cls.is_trans_str_type():
            return str(self.trans_str_value)
