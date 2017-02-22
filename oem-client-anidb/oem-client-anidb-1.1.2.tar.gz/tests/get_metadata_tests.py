from tests.fixtures import client


def test_match(client):
    assert client['anidb'].to('tvdb').get_metadata('1') is not None


def test_invalid(client):
    assert client['anidb'].to('tvdb').get_metadata('INVALID') is None
