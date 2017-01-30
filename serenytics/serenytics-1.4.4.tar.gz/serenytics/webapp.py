import json
import logging

from serenytics.user_preferences import UserPreferences
from .helpers import make_request
from . import settings

logger = logging.getLogger(__name__)


class WebApp(object):
    """
    Serenytics web app (dashboard)
    """

    def __init__(self, config, client):
        self._config = config
        self._client = client
        self._headers = client._headers

    @property
    def name(self):
        return self._config['name']

    @property
    def uuid(self):
        return self._config['uuid']

    @property
    def folder_name(self):
        folder_id = self._config['jsonContent'].get('folder')
        if folder_id is None:
            return UserPreferences.HOME_FOLDER
        return self._client.preferences._get_folder_from_id(folder_id, 'webapp')['name']

    def set_custom_css(self, css):
        """
        Apply given `css` to the web app.
        """
        self._config['jsonContent']['cssContent'] = css

    def set_custom_html_header(self, html):
        """
        Apply the given html header to the web app instead of just using the name by default.
        """
        self._config['jsonContent']['headerMode'] = 'custom_html'
        self._config['jsonContent']['htmlHeader'] = html

    def save(self):
        make_request('PUT', settings.SERENYTICS_API_DOMAIN + '/api/web_app/' + self.uuid,
                     data=json.dumps(self._config),
                     headers=self._headers)
