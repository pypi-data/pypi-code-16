import requests
import xml.dom.minidom as minidom
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from cbr.models import CBRCurrency, CBRCurrencyRate


class Command(BaseCommand):
    def load_cbr(self):
        url = 'http://www.cbr.ru/scripts/XML_daily.asp'

        resp = requests.get(url)
        doc = minidom.parseString(resp.content.decode('cp1251'))

        # Date parsing
        valcurs = doc.getElementsByTagName('ValCurs')[0]
        date_rate = valcurs.attributes.get('Date').value
        date_rate = datetime.strptime(date_rate, '%d.%m.%Y')

        # Rate parsing
        valutes = doc.getElementsByTagName('Valute')
        for v in valutes:
            code = v.attributes.get('ID').value
            num_code = v.getElementsByTagName('NumCode')[0].childNodes[0].data
            char_code = v.getElementsByTagName('CharCode')[0].childNodes[0].data
            nominal = v.getElementsByTagName('Nominal')[0].childNodes[0].data
            name = v.getElementsByTagName('Name')[0].childNodes[0].data
            rate = v.getElementsByTagName('Value')[0].childNodes[0].data

            nominal = int(nominal)
            rate = Decimal(rate.replace(',', '.'))

            currency, created = CBRCurrency.objects.get_or_create(
                code=code, defaults={'name': name, 'num_code': num_code, 'char_code': char_code})
            course, created = CBRCurrencyRate.objects.get_or_create(
                currency=currency, date_rate=date_rate, defaults={'nominal': nominal, 'rate': rate})

    def handle(self, *args, **options):
        self.load_cbr()
