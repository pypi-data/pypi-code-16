from datetime import date, datetime
from dateutil.parser import parse
from decimal import Decimal

from amaascore.assets.asset import Asset


class BondBase(Asset):

    @staticmethod
    def mandatory_attributes():
        return ['coupon', 'issue_date', 'par']

    def __init__(self, asset_manager_id, asset_id, maturity_date, coupon, par, asset_issuer_id,
                 asset_status, description, country_id, venue_id, client_id, issue_date, references={}, *args, **kwargs):
        self.asset_class = 'Bond'
        self.issue_date = issue_date
        self.coupon = coupon
        self.par = par
        super(BondBase, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                       asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                       description=description, country_id=country_id, venue_id=venue_id,
                                       maturity_date=maturity_date, references=references,
                                       client_id=client_id, *args, **kwargs)

    @property
    def issue_date(self):
        if hasattr(self, '_issue_date'):
            return self._issue_date

    @issue_date.setter
    def issue_date(self, issue_date):
        """
        The date on which the bond was issued.
        :param issue_date:
        :return:
        """
        if issue_date:
            self._issue_date = parse(issue_date).date() if isinstance(issue_date, (str, unicode)) else issue_date

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

    @property
    def defaulted(self):
        if hasattr(self, '_defaulted'):
            return self._defaulted

    @defaulted.setter
    def defaulted(self, defaulted):
        """
        Indicator of whether or not this bond has defaulted
        :param par:
        :return:
        """
        if defaulted is not None:
            self._defaulted = defaulted


class BondGovernment(BondBase):

    def __init__(self, asset_manager_id, asset_id, maturity_date=None, coupon=None, par=None,
                 asset_issuer_id=None, asset_status='Active', description='', country_id=None, venue_id=None,
                 client_id=None, issue_date=None, references={}, *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        super(BondGovernment, self).__init__(asset_manager_id=self.asset_manager_id, asset_id=asset_id,
                                             asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                             description=description, country_id=country_id, venue_id=venue_id,
                                             maturity_date=maturity_date, references=references, client_id=client_id,
                                             coupon=coupon, par=par, issue_date=issue_date, *args, **kwargs)


class BondCorporate(BondBase):

    def __init__(self, asset_manager_id, asset_id, maturity_date=None, coupon=None, par=None,
                 asset_issuer_id=None, asset_status='Active', description='', country_id=None, venue_id=None,
                 client_id=None, issue_date=None, references={}, *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        super(BondCorporate, self).__init__(asset_manager_id=self.asset_manager_id, asset_id=asset_id,
                                            asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                            description=description, country_id=country_id, venue_id=venue_id,
                                            maturity_date=maturity_date, references=references, client_id=client_id,
                                            coupon=coupon, par=par, issue_date=issue_date, *args, **kwargs)


class BondMortgage(BondBase):

    def __init__(self, asset_manager_id, asset_id, maturity_date=None, coupon=None, par=None,
                 asset_issuer_id=None, asset_status='Active', description='', country_id=None, venue_id=None,
                 client_id=None, issue_date=None, references={}, *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        super(BondMortgage, self).__init__(asset_manager_id=self.asset_manager_id, asset_id=asset_id,
                                           asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                           description=description, country_id=country_id, venue_id=venue_id,
                                           maturity_date=maturity_date, references=references, client_id=client_id,
                                           coupon=coupon, par=par, issue_date=issue_date, *args, **kwargs)
