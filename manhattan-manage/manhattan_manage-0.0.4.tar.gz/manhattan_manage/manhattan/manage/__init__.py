import flask
import jinja2

from manhattan.assets import Asset
from manhattan.manage.views.assets.upload import upload_chains as upload


class Manage:
    """
    The `Manage` class provides the initialization code for the package.
    """

    def __init__(self, app):
        self._app = app

        # Set-up a hidden blueprint to provide access to the templates
        blueprint = flask.Blueprint(
            '_manhattan_manage',
            __name__,
            template_folder='templates'
            )
        self._app.register_blueprint(blueprint)

    def manage_assets(self, root, backend, settings=None, path='/cms/'):
            """Set up support for managing assets"""

            # Configure the URL root for assets
            Asset._asset_root = root

            # Set up the asset manager
            self._app.asset_mgr = backend.AssetMgr(**(settings or {}))

            # Set up views for managing assets

            # Upload
            self._app.add_url_rule(
                path + 'upload-asset',
                endpoint='manage__upload_asset',
                view_func=upload.copy().flask_view(),
                methods=['POST']
                )

            # @@ Other views to come...