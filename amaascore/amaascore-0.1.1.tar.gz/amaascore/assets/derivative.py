from datetime import date, datetime
from dateutil import parser
from decimal import Decimal

from amaascore.assets.asset import Asset


class Derivative(Asset):

    def __init__(self, asset_manager_id, asset_id, maturity_date=None, asset_issuer_id=None, asset_status='Active',
                 description='', country_id=None, venue_id=None, client_id=None, issue_date=None, references={},
                 *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'Derivative'
        self.issue_date = issue_date

        super(Derivative, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=False,
                                         asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                         description=description, country_id=country_id, venue_id=venue_id,
                                         maturity_date=maturity_date, references=references, client_id=client_id,
                                         *args, **kwargs)
