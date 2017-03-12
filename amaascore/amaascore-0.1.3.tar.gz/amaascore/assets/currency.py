from amaascore.assets.asset import Asset


class Currency(Asset):

    def __init__(self, asset_id, deliverable, asset_status='Active', minor_unit_places=2, description='',
                 country_id=None, *args, **kwargs):
        self.asset_class = 'Currency'
        self.deliverable = deliverable
        self.minor_unit_places = minor_unit_places
        super(Currency, self).__init__(asset_manager_id=0, asset_id=asset_id, fungible=True,
                                       asset_class=self.asset_class, asset_status=asset_status, description=description,
                                       country_id=country_id, venue_id=None, maturity_date=None,
                                       *args, **kwargs)
