from amaascore.assets.asset import Asset


class Currency(Asset):

    def __init__(self, asset_manager_id, asset_id, asset_status='Active', description='', country_id=None,
                 client_id=None, references={}, *args, **kwargs):
        self.asset_class = 'Currency'

        super(Currency, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                       asset_class=self.asset_class, asset_status=asset_status, description=description,
                                       country_id=country_id, venue_id=None, maturity_date=None, references=references,
                                       client_id=client_id, *args, **kwargs)
