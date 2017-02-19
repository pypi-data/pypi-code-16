from blockchain import exchangerates
from django.db import models


class BTCRates(models.Model):
    pass



    def get_rates(self):
        ticker = exchangerates.get_ticker()
        # print the 15 min price for every currency
        for k in ticker:
            print(k, ticker[k].p15min)
