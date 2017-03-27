from __future__ import unicode_literals

from mock import mock, patch

from mopidy_auto import Extension


def test_get_default_config():
    ext = Extension()

    config = ext.get_default_config()

    assert '[auto]' in config
    assert 'enabled = true' in config


def test_get_config_schema():
    ext = Extension()

    schema = ext.get_config_schema()
    assert 'base_path' in schema
    assert 'max_tracks' in schema
    for index in range(3):
        assert "s{}_hour".format(index) in schema
        assert "s{}_minute".format(index) in schema
        assert "s{}_folder".format(index) in schema
        assert "s{}_max_volume".format(index) in schema


# TODO Write more test
def test_get_section_by_time():
    import datetime

    frontend = frontend.MyFrontend.start(config(), self.core).proxy()

    with patch('datetime.datetime') as mock_date:
        mock_date.now.return_value = datetime.datetime(2017, 3, 25, 8, 0, 0, 0)

        section = get_section_by_time()

        assert 'Rap' == section['folder']
        assert '50' == section['max_volume']
