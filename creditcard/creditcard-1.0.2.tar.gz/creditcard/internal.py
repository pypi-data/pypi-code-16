# coding: UTF-8
# Copyright © 2017 Alex Forster. All rights reserved.

import math
import pkg_resources

from datetime import datetime
from xml.etree.ElementTree import ElementTree


class CreditCard(object):

    _registry = None  # type: dict

    @staticmethod
    def _load_registry(filename):

        et = ElementTree(element='registry', file=filename)

        registry = []

        for card in et.getroot().findall('card'):

            spec = dict(card.items())

            if 'id' in spec:

                spec['id'] = spec['id'].strip()

            if 'brand' in spec:

                spec['brand'] = spec['brand'].strip()

            if 'prefix' in spec:

                spec['prefix'] = [el.strip().split('-') for el in spec['prefix'].strip().split(',')]
                spec['prefix'] = [range(int(el[0]),int(el[1])+1) if len(el) == 2 else el for el in spec['prefix']]
                spec['prefix'] = [str(el) for sublist in spec['prefix'] for el in sublist]

            if 'length' in spec:

                spec['length'] = [int(el.strip()) for el in spec['length'].strip().split(',')]

            if 'mask' in spec:

                spec['mask'] = [int(el.strip()) for el in spec['mask'].strip().split(',')]

            if 'code.name' in spec:

                spec.setdefault('code', {})
                spec['code']['name'] = spec['code.name']
                spec.pop('code.name')

            if 'code.length' in spec:

                spec.setdefault('code', {})
                spec['code']['length'] = int(spec['code.length'])
                spec.pop('code.length')

            if 'luhn' in spec:

                spec['luhn'] = bool(spec['luhn'].strip())

            registry.append(spec)

        CreditCard._registry = registry

    @staticmethod
    def _lookup_registry(number):

        for card in CreditCard._registry:

            if any(number.startswith(prefix) for prefix in card['prefix']):

                return card

        return None

    @staticmethod
    def _luhn(number):

        sum = 0
        num_digits = len(number)
        oddeven = num_digits & 1

        for count in range(0, num_digits):

            digit = int(number[count])

            if not ((count & 1) ^ oddeven):
                digit *= 2
            if digit > 9:
                digit -= 9

            sum += digit

        return (sum % 10) == 0

    def __init__(self, number, expire_month=None, expire_year=None, code=None, cardholder=None):

        self._number = str(int(number)).strip()
        self._expire_month = str(int(expire_month)).strip() if expire_month else None
        self._expire_year = str(int(expire_year)).strip() if expire_year else None
        self._expire_year = \
            str(int(math.floor(datetime.now().year/100)))+self._expire_year if expire_year and len(expire_year) == 2 \
            else self._expire_year if expire_year and len(expire_year) == 4 \
            else None
        self._code = str(int(code)).strip() if code else None
        self._cardholder = str(cardholder).strip() if cardholder else None

        if CreditCard._registry is None:

            registry_data_file = pkg_resources.resource_filename('creditcard', 'data/registry.xml')

            CreditCard._load_registry(registry_data_file)

    @property
    def is_valid(self):

        registry = CreditCard._lookup_registry(self._number)
        if not registry: return False  # no card type has this prefix

        if len(self._number) not in registry['length']:

            return False  # the card number's length is invalid for this card type

        if registry['luhn'] and not CreditCard._luhn(self._number):

            return False  # this card number has an invalid checksum

        if self._expire_month and (int(self._expire_month) < 1 or int(self._expire_month) > 12):

            return False  # this card's expiration month is invalid

        year = datetime.now().year

        if self._expire_year and (int(self._expire_year) < year-20 or int(self._expire_year) > year+20):

            return False  # this card's expiration year is invalid

        if self._code and len(self._code) != registry['code']['length']:

            return False  # this card's verification code is the wrong length

        return True

    @property
    def brand(self):

        registry = CreditCard._lookup_registry(self._number)
        if not registry: return None  # no card type has this prefix

        return registry['brand']

    @property
    def cardholder(self):

        if not self._cardholder: return None

        return self._cardholder

    @property
    def number(self):

        registry = CreditCard._lookup_registry(self._number)
        if not registry: return self._number

        number_tmp = self._number
        result = []

        for m in registry['mask']:

            part, number_tmp = number_tmp[:m], number_tmp[m:]
            result.append(part)

        return ' '.join(result)

    @property
    def expires(self):

        if not self._expire_month or not self._expire_year: return None

        return datetime(int(self._expire_year), int(self._expire_month), 1).date()

    @property
    def expires_string(self):

        expires = self.expires
        if not expires: return None

        return '{:02d}/{:02d}'.format(expires.month, expires.year - 2000)

    @property
    def is_expired(self):

        expires = self.expires
        if not expires: return None

        return datetime.now().date() >= expires

    @property
    def code_name(self):

        registry = CreditCard._lookup_registry(self._number)
        if not registry: return None  # no card type has this prefix

        return registry['code']['name']

    @property
    def code(self):

        if not self._code: return None

        return self._code
