from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import inspect

#  All possible class names must be inserted into the globals collection.
#  If there is a better way of doing this, please suggest!
from amaascore.parties.broker import Broker
from amaascore.parties.company import Company
from amaascore.parties.exchange import Exchange
from amaascore.parties.fund import Fund
from amaascore.parties.government_agency import GovernmentAgency
from amaascore.parties.individual import Individual
from amaascore.parties.organisation import Organisation
from amaascore.parties.party import Party


def json_to_party(json_to_convert):
    # Iterate through the party children, converting the various JSON attributes into the relevant class type
    for (collection_name, clazz) in Party.children().items():
        children = json_to_convert.pop(collection_name, {})
        collection = {}
        for (child_type, child_json) in children.items():
            # Handle the case where there are multiple children for a given type - e.g. links
            if isinstance(child_json, list):
                child = set()
                for child_json_in_list in child_json:
                    child.add(clazz(**child_json_in_list))
            else:
                child = clazz(**child_json)
            collection[child_type] = child
        json_to_convert[collection_name] = collection
    clazz = globals().get(json_to_convert.get('party_type'))
    args = inspect.getargspec(clazz.__init__)
    # Some fields are always added in, even though they're not explicitly part of the constructor
    clazz_args = args.args + clazz.amaas_model_attributes()
    # is not None is important so it includes zeros and False
    constructor_dict = {arg: json_to_convert.get(arg) for arg in clazz_args
                        if json_to_convert.get(arg) is not None and arg != 'self'}
    party = clazz(**constructor_dict)
    return party


def csv_filename_to_parties(filename):
    with open(filename, 'rb') as f:
        parties = csv_stream_to_parties(f)
    return parties


def csv_stream_to_parties(stream):
    reader = csv.DictReader(stream)
    parties = []
    for row in reader:
        parties.append(json_to_party(row))
    return parties


def parties_to_csv(parties, filename):
    with open(filename, 'w') as csvfile:
        parties_to_csv_stream(parties=parties, stream=csvfile)


def parties_to_csv_stream(parties, stream):
    if not parties:
        return
    party_dicts = []
    for party in parties:
        party_dict = party.to_json()
        # FOR NOW - remove all children
        [party_dict.pop(child, None) for child in Party.children().keys()]
        party_dicts.append(party_dict)
    fieldnames = party_dicts[0].keys()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(party_dicts)
