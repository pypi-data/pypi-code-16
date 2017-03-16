from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class CBRCurrency(models.Model):
    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(_('Name'), max_length=255)
    code = models.SlugField(unique=True)
    num_code = models.SlugField()
    char_code = models.SlugField()


@python_2_unicode_compatible
class CBRCurrencyRate(models.Model):
    class Meta:
        verbose_name = _('Rate of currency')
        verbose_name_plural = _('Rates of currency')
        ordering = ['date_rate']

    def __str__(self):
        return '{} - {}'.format(self.date_rate, self.rate)

    currency = models.ForeignKey(CBRCurrency, verbose_name=_('Currency'))
    date_rate = models.DateField(_('Date of rate'), db_index=True)
    nominal = models.PositiveSmallIntegerField(_('Nominal'))
    rate = models.DecimalField(_('Rate'), max_digits=10, decimal_places=4)
