import json
import uuid

import pytest

from serenytics import settings
from serenytics.helpers import make_request
from tests.common import create_webapp


class TestWebApp(object):

    @pytest.fixture(autouse=True)
    def set_test_client(self, serenytics_client):
        self._client = serenytics_client

    def test_folders(self):
        # create new folder (saved in user preferences)
        preferences = self._client.preferences._preferences
        folder_id = str(uuid.uuid4())
        folder_name = 'Test ' + folder_id
        if 'webappsFolders' not in preferences:
            preferences['webappsFolders'] = []
        preferences['webappsFolders'].append({'id': folder_id, 'name': folder_name})
        make_request('put', settings.SERENYTICS_API_DOMAIN + '/api/me/preferences',
                     data=json.dumps(preferences),
                     headers=self._client._headers)

        # reset preferences cache
        self._client._preferences = None

        # create webapp in folder
        create_webapp(client=self._client, name='Test webapp', json_content={'folder': folder_id})

        # check webapp and folder
        webapps = self._client.get_webapps()
        webapps_in_folder = [webapp for webapp in webapps if webapp.folder_name == folder_name]
        assert len(webapps_in_folder) == 1
