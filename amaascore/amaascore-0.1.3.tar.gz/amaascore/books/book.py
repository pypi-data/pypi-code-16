from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import uuid

from amaascore.core.amaas_model import AMaaSModel


class Book(AMaaSModel):

    @staticmethod
    def non_interface_attributes():
        return ['positions']

    def __init__(self, asset_manager_id, book_id=None, book_status='Active', owner_id=None, party_id=None,
                 close_time=datetime.timedelta(hours=18), timezone='UTC', description='', positions=None,
                 *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.book_id = book_id or uuid.uuid4().hex
        self.book_status = book_status
        self.owner_id = owner_id
        self.party_id = party_id
        self.close_time = close_time
        self.timezone = timezone
        self.description = description
        self.positions = positions
        super(Book, self).__init__(*args, **kwargs)

    def positions_by_asset(self):
        """
        A dictionary of Position objects keyed by asset_id.
        :return:
        """
        return {position.asset_id: position for position in self.positions}
