# -*- coding: utf-8 -*-
from cryptobalances.exchanges.poloniex import get_rates as poloniex_rates
from cryptobalances.exchanges.shapeshift import get_rates as shapeshift_rates
from cryptobalances.exchanges.changer import get_rates as changer_rates
from cryptobalances.exchanges.coinomat import get_rates as coinomat_rates


__all__ = ['poloniex_rates', 'shapeshift_rates', 'changer_rates', 'coinomat_rates']
