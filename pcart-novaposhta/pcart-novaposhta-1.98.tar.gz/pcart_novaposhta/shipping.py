from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from pcart_cart.shipping import BaseShipping
from .models import Area, City, Office


class NovaPoshtaShippingForm(forms.Form):
    def __init__(self, nv_api_key, *args, **kwargs):
        super(NovaPoshtaShippingForm, self).__init__(*args, **kwargs)
        _data = self.data.copy()

        # Areas
        areas = Area.objects.all().values('id', 'description')
        area_choices = [(None, '-----')]
        area_choices += [(x['id'], x['description']) for x in areas]

        self.fields['area'] = forms.ChoiceField(
            label=_('Region'),
            choices=area_choices,
            required=False,
        )

        if 'area' in _data:
            cities = City.objects.filter(area_id=_data['area']).values('id', 'description')
            city_choices = [(None, '-----')]
            city_choices += [(x['id'], x['description']) for x in cities]

            self.fields['city'] = forms.ChoiceField(
                label=_('City'),
                choices=city_choices,
                required=False,
            )

        if 'city' in _data:
            offices = Office.objects.filter(city_id=_data['city']).values('id', 'description')
            office_choices = [(x['id'], x['description']) for x in offices]
            self.fields['office'] = forms.ChoiceField(
                label=_('Office'),
                choices=office_choices,
                required=False,
            )


class NovaPoshtaShipping(BaseShipping):
    title = _('Nova Poshta')

    def __init__(self, config={}):
        super(NovaPoshtaShipping, self).__init__(config)
        self.api_key = config.get('api_key', getattr(settings, 'PCART_NOVAPOSHTA_API_KEY', ''))

    def get_form(self, request, *args, **kwargs):
        if self.api_key is not None:
            form = NovaPoshtaShippingForm(self.api_key, *args, **kwargs)
            return form
