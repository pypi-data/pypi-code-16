from __future__ import absolute_import, division, print_function, unicode_literals

import random

from amaascore.core.reference import Reference
from amaascore.parties.broker import Broker
from amaascore.parties.children import Address, Email
from amaascore.parties.individual import Individual
from amaascore.parties.party import Party
from amaascore.tools.helpers import random_string


def generate_common(asset_manager_id, party_id, party_status):
    common = {'asset_manager_id': asset_manager_id or random.randint(1, 1000),
              'party_id': party_id or str(random.randint(1, 1000)),
              'party_status': party_status or 'Active'
              }

    return common


def generate_party(asset_manager_id=None, party_id=None, party_status=None):
    references = {'PartyDB': Reference(random_string(10))}
    attributes = generate_common(asset_manager_id=asset_manager_id, party_id=party_id, party_status=party_status)
    party = Party(**attributes)
    # Does this screw up the party due to mutability concerns?  Do some testing.
    party.references.update(references)
    party.upsert_address('Registered', generate_address(address_primary=True))
    party.upsert_email('Office', generate_email(email_primary=True))
    return party


def generate_broker(asset_manager_id=None, party_id=None, party_status=None):
    references = {'LEI': Reference(random_string(10))}
    attributes = generate_common(asset_manager_id=asset_manager_id, party_id=party_id, party_status=party_status)
    broker = Broker(**attributes)
    # Does this screw up the party due to mutability concerns?  Do some testing.
    broker.references.update(references)
    broker.upsert_address('Registered', generate_address(address_primary=True))
    broker.upsert_email('Office', generate_email(email_primary=True))
    return broker


def generate_individual(asset_manager_id=None, party_id=None, party_status=None):
    attributes = generate_common(asset_manager_id=asset_manager_id, party_id=party_id, party_status=party_status)
    individual = Individual(**attributes)
    return individual


def generate_address(country_id=None, address_primary=False):
    address = Address(line_one=random_string(20),
                      line_two=random.choice([None, random_string(10)]),
                      city=random_string(10),
                      region=random_string(10),
                      postal_code=random_string(6),
                      country_id=country_id or random_string(3),  # Make this a real country code
                      address_primary=address_primary)
    return address


def generate_email(email=None, email_primary=False):
    return Email(email=email or (random_string(10) + '@amaas.com'), email_primary=email_primary)
