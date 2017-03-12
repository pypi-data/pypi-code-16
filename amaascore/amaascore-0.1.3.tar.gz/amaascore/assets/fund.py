from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, date
from dateutil import parser
import sys

from amaascore.assets.asset import Asset

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Fund(Asset):

    def __init__(self, asset_manager_id, asset_id, asset_issuer_id=None, asset_status='Active', description='',
                 country_id=None, venue_id=None, currency=None, creation_date=None,
                 links={}, references={},
                 *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'Fund'
        self.creation_date = creation_date
        super(Fund, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                   asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                   description=description, country_id=country_id, venue_id=venue_id,
                                   currency=currency, links=links, references=references, *args, **kwargs)

    #  Perhaps this comes from the linked Fund
    @property
    def creation_date(self):
        if hasattr(self, '_creation_date'):
            return self._creation_date

    @creation_date.setter
    def creation_date(self, value):
        """
        The date on which the bond was issued.
        :param creation_date:
        :return:
        """
        if value:
            self._creation_date = parse(value).date() if isinstance(value, type_check) else value
