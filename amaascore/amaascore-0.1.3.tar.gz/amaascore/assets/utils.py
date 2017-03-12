from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import inspect

#  All possible class names must be inserted into the globals collection.
#  If there is a better way of doing this, please suggest!
from amaascore.assets.asset import Asset
from amaascore.assets.bond import BondCorporate, BondGovernment, BondMortgage
from amaascore.assets.bond_option import BondOption
from amaascore.assets.currency import Currency
from amaascore.assets.derivative import Derivative
from amaascore.assets.equity import Equity
from amaascore.assets.foreign_exchange import ForeignExchange, NonDeliverableForward


def json_to_asset(json_asset):
    # Iterate through the asset children, converting the various JSON attributes into the relevant class type
    for (collection_name, clazz) in Asset.children().items():
        children = json_asset.pop(collection_name, {})
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
        json_asset[collection_name] = collection
    clazz = globals().get(json_asset.get('asset_type'))
    args = inspect.getargspec(clazz.__init__)
    # Some fields are always added in, even though they're not explicitly part of the constructor
    clazz_args = args.args + clazz.amaas_model_attributes()
    # is not None is important so it includes zeros and False
    constructor_dict = {arg: json_asset.get(arg) for arg in clazz_args
                        if json_asset.get(arg) is not None and arg != 'self'}
    asset = clazz(**constructor_dict)
    return asset


def csv_filename_to_assets(filename):
    with open(filename, 'rb') as f:
        assets = csv_stream_to_assets(f)
    return assets


def csv_stream_to_assets(stream):
    reader = csv.DictReader(stream)
    assets = []
    for row in reader:
        assets.append(json_to_asset(row))
    return assets


def assets_to_csv(assets, filename):
    with open(filename, 'w') as csvfile:
        assets_to_csv_stream(assets=assets, stream=csvfile)


def assets_to_csv_stream(assets, stream):
    if not assets:
        return
    asset_dicts = []
    for asset in assets:
        asset_dict = asset.to_json()
        # FOR NOW - remove all children
        [asset_dict.pop(child, None) for child in asset.children().keys()]
        asset_dicts.append(asset_dict)
    fieldnames = asset_dicts[0].keys()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(asset_dicts)
