from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.module_loading import import_string


def shipping_method_choices():
    shipping_methods = list()
    for m in settings.PCART_SHIPPING_METHODS:
        _shipping_method_class = import_string(m['backend'])
        _shipping_method = _shipping_method_class(config=m['config'])
        shipping_methods.append((m['name'], _shipping_method.get_title()))
    return shipping_methods


def payment_method_choices():
    payment_methods = list()
    for m in settings.PCART_PAYMENT_METHODS:
        _payment_method_class = import_string(m['backend'])
        _payment_method = _payment_method_class(config=m['config'])
        payment_methods.append((m['name'], _payment_method.get_title()))
    return payment_methods


class OrderCheckoutForm(forms.Form):
    name = forms.CharField(label=_('Name'), required=True)
    email = forms.EmailField(label=_('Email'), required=True)
    phone = forms.CharField(label=_('Phone'), required=True)

    shipping_method = forms.ChoiceField(label=_('Shipping method'), choices=shipping_method_choices)
    payment_method = forms.ChoiceField(label=_('Payment method'), choices=payment_method_choices)

    note = forms.CharField(label=_('Note'), widget=forms.Textarea, required=False)
    accept_toc = forms.BooleanField(label=_('Accept terms of condition'))

    def __init__(self, *args, **kwargs):
        super(OrderCheckoutForm, self).__init__(*args, **kwargs)
