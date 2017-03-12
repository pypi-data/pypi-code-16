from datetime import date
from dateutil.parser import parse
from decimal import Decimal

from amaascore.assets.asset import Asset


class BondBase(Asset):

    def __init__(self, asset_manager_id, asset_id, maturity_date, coupon, par, pay_frequency, asset_issuer_id,
                 asset_status, description, country_id, venue_id, issue_date, defaulted, links, references,
                 *args, **kwargs):
        self.asset_class = 'Bond'
        self.coupon = coupon
        self.par = par
        self.pay_frequency = pay_frequency
        self.defaulted = defaulted
        super(BondBase, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                       asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                       description=description, country_id=country_id, venue_id=venue_id,
                                       issue_date=issue_date, maturity_date=maturity_date, links=links,
                                       references=references,
                                       *args, **kwargs)

    @property
    def coupon(self):
        if hasattr(self, '_coupon'):
            return self._coupon

    @coupon.setter
    def coupon(self, coupon):
        """
        The coupon paid out by the bond.  Represented as a fraction of 1 (e.g. 0.05 is 5%).
        :param coupon:
        :return:
        """
        if coupon is not None:
            self._coupon = Decimal(coupon)

    @property
    def par(self):
        if hasattr(self, '_par'):
            return self._par

    @par.setter
    def par(self, par):
        """
        The face value of each bond.
        Force this to be Decimal
        :param par:
        :return:
        """
        if par is not None:
            self._par = Decimal(par)


class BondGovernment(BondBase):

    def __init__(self, asset_manager_id, asset_id, coupon, par, pay_frequency, defaulted=False, asset_issuer_id=None,
                 maturity_date=date.max, asset_status='Active', description='', country_id=None, venue_id=None,
                 issue_date=date.min, links={}, references={}, *args, **kwargs):
        super(BondGovernment, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                             asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                             description=description, country_id=country_id, venue_id=venue_id,
                                             maturity_date=maturity_date, links=links, references=references,
                                             coupon=coupon, par=par, issue_date=issue_date, pay_frequency=pay_frequency,
                                             defaulted=defaulted, *args, **kwargs)


class BondCorporate(BondBase):

    def __init__(self, asset_manager_id, asset_id, coupon, par, pay_frequency, defaulted=False, asset_issuer_id=None,
                 maturity_date=date.max, asset_status='Active', description='', country_id=None, venue_id=None,
                 issue_date=date.min, links={}, references={}, *args, **kwargs):
        super(BondCorporate, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                            asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                            description=description, country_id=country_id, venue_id=venue_id,
                                            maturity_date=maturity_date, links=links, references=references,
                                            coupon=coupon, par=par, issue_date=issue_date, pay_frequency=pay_frequency,
                                            defaulted=defaulted, *args, **kwargs)


class BondMortgage(BondBase):

    def __init__(self, asset_manager_id, asset_id, coupon, par, pay_frequency, defaulted=False, asset_issuer_id=None,
                 maturity_date=date.max, asset_status='Active', description='', country_id=None, venue_id=None,
                 issue_date=date.min, links={}, references={}, *args, **kwargs):
        super(BondMortgage, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                           asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                           description=description, country_id=country_id, venue_id=venue_id,
                                           maturity_date=maturity_date, links=links, references=references,
                                           coupon=coupon, par=par, issue_date=issue_date, pay_frequency=pay_frequency,
                                           defaulted=defaulted, *args, **kwargs)
