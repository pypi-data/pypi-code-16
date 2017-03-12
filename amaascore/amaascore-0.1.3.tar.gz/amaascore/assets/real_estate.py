from datetime import datetime, date
from dateutil import parser

from amaascore.assets.real_asset import RealAsset


class RealEstate(RealAsset):

    def __init__(self, asset_manager_id, asset_id, asset_issuer_id=None, asset_status='Active', description='',
                 country_id=None, venue_id=None, currency=None, links={}, references={}, *args, **kwargs):
        super(RealEstate, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                         asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                         description=description, country_id=country_id, venue_id=venue_id,
                                         currency=currency, links=links, references=references,
                                         *args, **kwargs)
