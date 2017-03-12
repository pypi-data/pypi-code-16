from datetime import date
from decimal import Decimal

from amaascore.assets.asset import Asset
from amaascore.assets.option_mixin import OptionMixin


class ForeignExchangeOption(Asset, OptionMixin):
    """
    An over the counter Option with an underlying FX pair.
    """

    def __init__(self, asset_manager_id, asset_id, option_type, strike, premium, underlying_asset_id, option_style,
                 issue_date=date.min, maturity_date=date.max, asset_status='Active', asset_issuer_id=None,
                 description='', links={}, references={},
                 *args, **kwargs):
        self.asset_class = 'ForeignExchange'
        self.option_type = option_type
        self.strike = strike
        self.premium = premium
        self.underlying_asset_id = underlying_asset_id
        self.option_style = option_style
        super(ForeignExchangeOption, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                                    fungible=False, asset_issuer_id=asset_issuer_id,
                                                    issue_date=issue_date, maturity_date=maturity_date,
                                                    asset_status=asset_status, description=description,
                                                    links=links, references=references, *args, **kwargs)

