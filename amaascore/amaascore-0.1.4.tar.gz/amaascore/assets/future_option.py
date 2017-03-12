from decimal import Decimal

from amaascore.assets.future import Future
from amaascore.assets.option_mixin import OptionMixin


class FutureOption(Future, OptionMixin):

    def __init__(self, asset_manager_id, asset_id, option_type, option_style, strike, underlying_asset_id,
                 asset_issuer_id=None, asset_status='Active', issue_date=None, expiry_date=None, description='',
                 country_id=None, venue_id=None, links={}, references={}, *args, **kwargs):
        self.option_type = option_type
        self.option_style = option_style
        self.strike = strike
        self.underlying_asset_id = underlying_asset_id
        super(FutureOption, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                           asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                           description=description, country_id=country_id, venue_id=venue_id,
                                           links=links, references=references, issue_date=issue_date,
                                           expiry_date=expiry_date,
                                           *args, **kwargs)
