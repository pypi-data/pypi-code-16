from amaascore.assets.listed_derivative import ListedDerivative


class Future(ListedDerivative):

    def __init__(self, asset_manager_id, asset_id, asset_issuer_id=None, asset_status='Active', issue_date=None,
                 expiry_date=None, description='', country_id=None, venue_id=None, links={}, references={},
                 *args, **kwargs):
        super(Future, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                     asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                     description=description, country_id=country_id, venue_id=venue_id,
                                     links=links, references=references, issue_date=issue_date, expiry_date=expiry_date,
                                     *args, **kwargs)
