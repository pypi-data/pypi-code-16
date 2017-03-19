from __future__ import absolute_import, division, print_function, unicode_literals

import random

from amaascore.asset_managers.asset_manager import AssetManager
from amaascore.asset_managers.enums import ASSET_MANAGER_TYPES


def generate_asset_manager(asset_manager_id=None, asset_manager_type=None, client_id=None,
                           asset_manager_status='Active'):
    asset_manager = AssetManager(asset_manager_id=asset_manager_id,
                                 asset_manager_type=asset_manager_type or random.choice(ASSET_MANAGER_TYPES),
                                 client_id=client_id or random.randint(1, 2**31-1),
                                 asset_manager_status=asset_manager_status)
    return asset_manager
