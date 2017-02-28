# -*- coding: utf-8 -*-
from cryptobalances.checker import get_balance
from cryptobalances.checker import get_rate
from cryptobalances.validator import autodetect_currency


__all__ = ["get_balance", "autodetect_currency", "get_rate"]
__version__ = '0.9.3'
