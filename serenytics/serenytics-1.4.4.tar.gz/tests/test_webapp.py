import pytest


class TestWebApp(object):

    @pytest.fixture(autouse=True)
    def set_test_client(self, serenytics_client):
        self._client = serenytics_client

    def test_get_webapps(self):
        webapps = self._client.get_webapps()
        assert len(webapps) == 2

    def test_get_folder_name(self):
        webapps = self._client.get_webapps()
        folder_names = [webapp.folder_name for webapp in webapps]
        assert len(folder_names) == 2
        assert folder_names == self._client.preferences.webapp_folder_names
