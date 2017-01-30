# start by updating environment variables from .env file
from . import load_env  # noqa

from uuid import uuid4

import pytest

import serenytics
from serenytics.helpers import make_request, HTTP_204_NO_CONTENT
from serenytics.settings import load_environment_variable, SERENYTICS_API_DOMAIN, enable_log

enable_log()

SERENYTICS_API_KEY = load_environment_variable('SERENYTICS_API_KEY')
SERENYTICS_SCRIPT_ID = load_environment_variable('SERENYTICS_SCRIPT_ID')


def _delete_entity(entity, entity_name):
    entity_url = SERENYTICS_API_DOMAIN + '/api/' + entity_name + '/' + entity.uuid
    make_request('delete', entity_url, expected_status_code=HTTP_204_NO_CONTENT, headers=entity._headers)


@pytest.fixture(scope='session', autouse=True)
def serenytics_client():
    client = serenytics.Client(api_key=SERENYTICS_API_KEY,
                               script_id=SERENYTICS_SCRIPT_ID)
    return client


@pytest.yield_fixture(scope='function')
def storage_data_source(serenytics_client):
    name = 'test_' + str(uuid4())
    data_source = serenytics_client.get_or_create_storage_data_source_by_name(name)
    assert data_source.name == name

    yield data_source

    _delete_entity(data_source, 'data_source')


@pytest.yield_fixture(scope='session', autouse=True)
def script_test(serenytics_client):
    script = serenytics_client.get_script_by_uuid(SERENYTICS_SCRIPT_ID)
    assert script.uuid == SERENYTICS_SCRIPT_ID

    yield script
