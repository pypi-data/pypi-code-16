import os

import pytest
import requests_mock

from penapi.pentaho import Pentaho
from tests import FIXTURES_DIR


@pytest.fixture
def list_users():
    with open(os.path.join(FIXTURES_DIR, 'users_api.xml'), 'r') as fixture_file:
        data = fixture_file.read().replace('\n', '')
    return data


@pytest.fixture
def pentaho():
    pentaho = Pentaho(pentaho_base_url='http://test.com')
    return pentaho


@requests_mock.Mocker(kw='mock_api')
def test_user_api_list_success(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/users', text=list_users())
    user_list = pentaho.users.list()
    assert len(user_list) == 6


@requests_mock.Mocker(kw='mock_api')
def test_user_api_list_fail(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/users', text='', status_code=500)
    user_list = pentaho.users.list()
    assert len(user_list) == 0


@requests_mock.Mocker(kw='mock_api')
def test_user_api_create_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/createUser', text='')
    success = pentaho.users.create('test', 'pass')
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_user_api_create_fail(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/createUser', text='', status_code=412)
    success = pentaho.users.create('test', 'pass')
    assert not success


def test_user_api_create_fail_2(pentaho=pentaho()):
    with pytest.raises(ValueError):
        pentaho.users.create(username='test')


@requests_mock.Mocker(kw='mock_api')
def test_user_api_change_password_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/user', text='')
    success = pentaho.users.change_password('test', 'pass', 'pass')
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_user_api_change_password_fail(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/user', text='', status_code=403)
    success = pentaho.users.change_password('test', 'pass1', 'pass2')
    assert not success


@requests_mock.Mocker(kw='mock_api')
def test_user_api_delete_users_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/deleteUsers?userNames=test', text='')
    success = pentaho.users.delete('test')
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_user_api_delete_users_list_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/deleteUsers?userNames=test1%09test2', text='')
    success = pentaho.users.delete(['test1', 'test2'])
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_user_api_delete_users_fail(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/deleteUsers?userNames=test', text='', status_code=403)
    success = pentaho.users.delete('test')
    assert not success
