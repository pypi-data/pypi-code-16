from django import template

from cbr.models import CBRCurrencyRate

register = template.Library()


@register.inclusion_tag('cbr/informer.html', takes_context=True)
def currency_informer(context):
    usd = CBRCurrencyRate.objects.filter(currency__char_code='USD').last()
    eur = CBRCurrencyRate.objects.filter(currency__char_code='EUR').last()

    return {
        'request': context['request'],
        'usd': usd,
        'eur': eur,
    }
