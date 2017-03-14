
"""
Simple currency parser with Python
"""

from re import sub
from decimal import Decimal

__version__ = '0.3'


class Purrency(object):
    """Parser class."""

    def __init__(self, denomination):
        self.denomination = denomination
        self.parsed = self.parse(self.denomination)

    def parse(self, denomination):
        value = Decimal(sub(r'[^\d.]', '', denomination))

        #  TODO: Need to figure out how to implement regex without the .replace()
        currency = sub(r'[^\D]', '', denomination).replace(',', '').replace('.', '')
        return {'amount': value,
                'symbol': currency}
