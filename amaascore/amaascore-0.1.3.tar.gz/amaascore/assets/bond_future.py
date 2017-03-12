from datetime import date
from decimal import Decimal

from amaascore.assets.future import Future


class BondFuture(Future):

    def __init__(self, asset_manager_id, asset_id, expiry_date, underlying_bond_tenor, underlying_bond_coupon,
                 cheapest_to_deliver_id=None, asset_issuer_id=None, asset_status='Active', issue_date=date.min,
                 description='', country_id=None, venue_id=None, links={}, references={}, *args, **kwargs):
        """

        :param asset_manager_id: The asset manager who owns the data for this BondFuture
        :param asset_id: The owning asset manager's unique identifier for this BondFuture
        :param expiry_date: The date on which this BondFuture will expire
        :param underlying_bond_tenor: The tenor of the bond on which this is a future
        :param cheapest_to_deliver_id: Populated from the server, cannot be calculated in the SDK.
        :param asset_issuer_id: The owning asset manager's identifier for the issuer of this future
        :param asset_status: The status of this BondFuture
        :param issue_date: The date on which this BondFuture was created
        :param description: A human-readable description of this BondFuture
        :param country_id: The ISO 3166-1 alpha-3 code for the country that this BondFutureOption was issued in
        :param venue_id: The ISO-10383 identifier for the venue on which this BondFutureOption trades
        :param references: A dictionary of additional References for this BondFutureOption
        :param args:
        :param kwargs:
        """
        self.cheapest_to_deliver_id = cheapest_to_deliver_id
        self.expiry_date = expiry_date
        self.underlying_bond_tenor = underlying_bond_tenor
        self.underlying_bond_coupon = underlying_bond_coupon
        super(BondFuture, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                         asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                         description=description, country_id=country_id, venue_id=venue_id,
                                         links=links, references=references, issue_date=issue_date,
                                         *args, **kwargs)

    @property
    def underlying_bond_coupon(self):
        if hasattr(self, '_underlying_bond_coupon'):
            return self._underlying_bond_coupon

    @underlying_bond_coupon.setter
    def underlying_bond_coupon(self, underlying_bond_coupon):
        """
        The coupon paid out by the underlying bond.  Represented as a fraction of 1 (e.g. 0.05 is 5%).
        :param underlying_bond_coupon:
        :return:
        """
        if underlying_bond_coupon is not None:
            self._underlying_bond_coupon = Decimal(underlying_bond_coupon)

