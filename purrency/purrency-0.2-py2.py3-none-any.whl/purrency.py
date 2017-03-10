
"""
Simple currency parser with Python
"""

from re import sub
from decimal import Decimal

__version__ = '0.2'


class Purrency(object):
    """Parser class."""

    def __init__(self, denomination):
        self.denomination = denomination

    def parse(self):
        value = Decimal(sub(r'[^\d.]', '', self.denomination))

        #  TODO: Need to figure out how to implement regex without the .replace()
        currency = sub(r'[^\D]', '', self.denomination).replace(',', '').replace('.', '')
        return {'amount': value,
                'symbol': currency}
