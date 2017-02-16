import pytest

from kube import _error


@pytest.fixture
def err(cluster):
    try:
        cluster.proxy.get('api/v1', 'some-non-existing-resource')
    except _error.APIError as exc:
        return exc
    else:
        pytest.rail('No APIError exception')


def test_response(err):
    assert err.response.status_code == 404


def test_message(err):
    assert isinstance(err.message, str)
    assert err.message


def test_status_code(err):
    assert err.status_code == err.response.status_code


def test_str(err):
    assert str(err)
    assert str(err.status_code) in str(err)
    assert err.message in str(err)


def test_str_no_json(err):
    def json():
        raise Exception('oops')
    err.response.json = json
    assert str(err)
