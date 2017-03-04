# -*- coding: utf-8 -*-
from cryptobalances.checker import get_balance
from cryptobalances.checker import get_rate
from cryptobalances.validator import autodetect_currency
from cryptobalances.config import get_supported_currencies


__all__ = ["get_balance", "get_rate", "autodetect_currency", "get_supported_currencies"]
__version__ = '0.9.5'
