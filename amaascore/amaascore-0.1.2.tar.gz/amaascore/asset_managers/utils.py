from amaascore.asset_managers.asset_manager import AssetManager


def json_to_asset_manager(json_asset_manager):
    asset_manager = AssetManager(**json_asset_manager)
    return asset_manager
