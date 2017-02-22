import cryptox.public.get_currency_pairs.get_currency_pairs as cp
import cryptox.public.order_book.order_book as ob
import cryptox.public.trade_history.trade_history as th
import cryptox.public.day_volume.day_volume as dv

class Market():
    """
    Main object used to query various public endpoints
    """
    def get_currency_pairs(self):
        return cp.get_currency_pairs(self)

    def day_volume(self, currency_pairs=None):
        return dv.day_volume(self, currency_pairs)

    def order_book(self, depth=100):
        return ob.order_book(self, depth)

    def trade_history(self, depth=100):
        return th.trade_history(self, depth)

    def __init__(self, exchange='all', currency_pair=None):
        self.exchange = exchange
        self.currency_pair = currency_pair
        #consider allowing private endpoints in the future
        #consider adding websocket data