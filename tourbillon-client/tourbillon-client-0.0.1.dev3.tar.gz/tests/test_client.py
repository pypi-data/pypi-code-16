import pytest
import pandas as pd
from tourbillon_client import Client


@pytest.fixture
def client():
    c = Client('http://127.0.0.1:5000/')
    return c


@pytest.fixture
def sample_data():
    data = {
        '2016-11-03 01:00': 10,
        '2016-11-03 02:00': 20,
        '2016-11-03 04:00': 40,
        '2016-11-03 05:00': 50,
    }
    df = pd.DataFrame({'value': data})
    df.index = pd.to_datetime(df.index)
    return df


def test_create(client):
    assert client.create('ham')


def test_write(client, sample_data):
    assert client.write('ham', sample_data)


def test_read_write(client, sample_data):
    client.create('ham')
    client.write('ham', sample_data)
    result = client.read('ham', '2016-11-01', '2016-11-05')
    assert all(result == sample_data)


def test_delete(client):
    assert client.create('ham')
    assert client.delete('ham')
    assert not client.exists('ham')


def test_read_tail(client, sample_data):
    client.create('ham')
    client.write('ham', sample_data)
    result = client.read('ham', tail=2)
    assert result.shape == (2, 1), result
