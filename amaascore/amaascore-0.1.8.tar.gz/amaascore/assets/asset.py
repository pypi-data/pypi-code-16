from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.parser import parse
import sys
import uuid

from amaascore.core.amaas_model import AMaaSModel
from amaascore.core.reference import Reference

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Asset(AMaaSModel):

    @staticmethod
    def children():
        return {'references': Reference}

    def __init__(self, asset_manager_id, fungible, asset_issuer_id=None, asset_id=None, asset_status='Active',
                 country_id=None, venue_id=None, currency=None, issue_date=date.min, maturity_date=date.max,
                 description='', links={}, references={},
                 *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.asset_id = asset_id or uuid.uuid4().hex
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'Asset'
        self.asset_type = self.__class__.__name__
        self.fungible = fungible
        self.asset_issuer_id = asset_issuer_id
        self.asset_status = asset_status
        self.country_id = country_id
        self.venue_id = venue_id
        self.currency = currency
        self.issue_date = issue_date
        self.maturity_date = maturity_date
        self.description = description
        self.links = links
        self.references = references
        self.references['AMaaS'] = Reference(reference_value=self.asset_id)  # Upserts the AMaaS Reference

        super(Asset, self).__init__(*args, **kwargs)

    def reference_types(self):
        """
        TODO - are these helper functions useful?
        :return:
        """
        return self.references.keys()

    @property
    def issue_date(self):
        if hasattr(self, '_issue_date'):
            return self._issue_date

    @issue_date.setter
    def issue_date(self, value):
        """
        The date on which the asset is issued
        :param value:
        :return:
        """
        if value:
            self._issue_date = parse(value).date() if isinstance(value, type_check) else value

    @property
    def maturity_date(self):
        if hasattr(self, '_maturity_date'):
            return self._maturity_date

    @maturity_date.setter
    def maturity_date(self, value):
        """
        The date on which the asset matures and no longer holds value
        :param value:
        :return:
        """
        if value:
            self._maturity_date = parse(value).date() if isinstance(value, type_check) else value

    def __str__(self):
        return "Asset object - ID: %s" % self.asset_id
