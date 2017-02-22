from tests.fixtures import client


def test_match(client):
    assert client['anidb'].to('tvdb').get('1') is not None


def test_invalid(client):
    assert client['anidb'].to('tvdb').get('INVALID') is None
