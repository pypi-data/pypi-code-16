import os

import pytest
import requests_mock

from penapi.pentaho import Pentaho
from tests import FIXTURES_DIR


@pytest.fixture
def list_directory():
    with open(os.path.join(FIXTURES_DIR, 'list_directory.xml'), 'r') as fixture_file:
        data = fixture_file.read().replace('\n', '')
    return data


@pytest.fixture
def list_acl():
    with open(os.path.join(FIXTURES_DIR, 'list_acl.xml'), 'r') as fixture_file:
        data = fixture_file.read().replace('\n', '')
    return data


@pytest.fixture
def pentaho():
    pentaho = Pentaho(pentaho_base_url='http://test.com')
    return pentaho


@pytest.fixture
def pentaho_acl_dict():
    return {
        "entriesInheriting": False,
        "owner": "test@test.com",
        "ownerType": "1",
        "aces": [
            {
                "modifiable": True,
                "recipientType": 1,
                "permissions": [ 0 ],
                "recipient": "Authenticated"
            },
            {
                "modifiable": True,
                "recipientType": 1,
                "permissions": [ 4 ],
                "recipient": "Administrator"
            }
        ]
    }


@requests_mock.Mocker(kw='mock_api')
def test_files_api_list_success(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/repo/files/:home:dev:demo/tree?depth=3', text=list_directory())
    dir_tree = pentaho.files.list_directory("/home/dev/demo", depth=3)
    assert len(dir_tree['children']) == 8


@requests_mock.Mocker(kw='mock_api')
def test_files_api_list_acl_success(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/repo/files/:home:dev:demo/acl', text=list_acl())
    acl = pentaho.files.get_acl("/home/dev/demo")
    assert len(acl)


@requests_mock.Mocker(kw='mock_api')
def test_files_api_create_directory(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/repo/dirs/:home:dev:demo', text='', status_code=200)
    success = pentaho.files.create_directory("/home/dev/demo")
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_files_api_create_directory_exist(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/repo/dirs/:home:dev:demo', text='', status_code=409)
    success = pentaho.files.create_directory("/home/dev/demo")
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_files_api_create_directory_fail(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/repo/dirs/:home:dev:demo', text='', status_code=500)
    success = pentaho.files.create_directory("/home/dev/demo")
    assert not success


@requests_mock.Mocker(kw='mock_api')
def test_files_api_set_acl_success(mock_api, pentaho=pentaho(), pentaho_acl_dict=pentaho_acl_dict()):
    mock_api.put('http://test.com/pentaho/api/repo/files/:home:dev:demo/acl', text='', status_code=200)
    success = pentaho.files.set_acl("/home/dev/demo", pentaho_acl_dict)
    assert success

