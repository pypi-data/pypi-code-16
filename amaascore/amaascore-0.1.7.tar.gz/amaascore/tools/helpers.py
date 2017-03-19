from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import random
import string


def random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def random_decimal():
    return Decimal(random.random() * 100).quantize(Decimal('0.01'))
