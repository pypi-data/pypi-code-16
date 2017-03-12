from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import timedelta
from dateutil.parser import parse

from amaascore.core.amaas_model import AMaaSModel


class AssetManager(AMaaSModel):

    def __init__(self, asset_manager_type, asset_manager_id=None, asset_manager_status='Active', party_id=None,
                 default_book_owner_id=None, default_timezone='UTC', default_book_close_time=timedelta(hours=18),
                 *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.asset_manager_type = asset_manager_type
        self.asset_manager_status = asset_manager_status
        self.party_id = party_id
        self.default_book_owner_id = default_book_owner_id
        self.default_timezone = default_timezone
        self.default_book_close_time = default_book_close_time
        super(AssetManager, self).__init__(*args, **kwargs)
