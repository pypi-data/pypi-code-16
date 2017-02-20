import pytest
import requests_mock
import os

from penapi.pentaho import Pentaho
from tests import FIXTURES_DIR


def list_roles():
    with open(os.path.join(FIXTURES_DIR, 'roles_api.xml'), 'r') as fixture_file:
        data = fixture_file.read().replace('\n', '')
    return data


def list_one_role():
    with open(os.path.join(FIXTURES_DIR, 'one_role_api.xml'), 'r') as fixture_file:
        data = fixture_file.read().replace('\n', '')
    return data


def list_users():
    with open(os.path.join(FIXTURES_DIR, 'users_api.xml'), 'r') as fixture_file:
        data = fixture_file.read().replace('\n', '')
    return data


def list_perm_role_map():
    with open(os.path.join(FIXTURES_DIR, 'perm_role_map.xml'), 'r') as fixture_file:
        data = fixture_file.read().replace('\n', '')
    return data


@pytest.fixture
def pentaho():
    return Pentaho(pentaho_base_url='http://test.com')


@requests_mock.Mocker(kw='mock_api')
def test_role_api_list_user_role_success(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/userRoles?userName=test', text=list_roles())
    roles_list = pentaho.roles.list_for_user('test')
    assert len(roles_list) == 3


@requests_mock.Mocker(kw='mock_api')
def test_role_api_list_user_one_success(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/userRoles?userName=test', text=list_one_role())
    roles_list = pentaho.roles.list_for_user('test')
    assert len(roles_list) == 1


@requests_mock.Mocker(kw='mock_api')
def test_role_api_list_user_fail(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/userRoles?userName=test', text='', status_code=500)
    roles_list = pentaho.roles.list_for_user('test')
    assert len(roles_list) == 0


@requests_mock.Mocker(kw='mock_api')
def test_role_api_assign_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/assignRoleToUser?userName=test&roleNames=power', text='')
    success = pentaho.roles.assign_to_user('test', ['power'])
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_role_api_assign_fail(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/assignRoleToUser?userName=test&roleNames=power',
                 text='', status_code=403)
    success = pentaho.roles.assign_to_user('test', ['power'])
    assert not success


def test_role_api_assign_fail_2(pentaho=pentaho()):
    with pytest.raises(ValueError):
        pentaho.roles.assign_to_user('test', 'power')


@requests_mock.Mocker(kw='mock_api')
def test_role_api_remove_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/removeRoleFromUser?userName=test&roleNames=Business', text='')
    success = pentaho.roles.remove_from_user('test', ['Business'])
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_role_api_remove_fail(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/removeRoleFromUser?userName=test&roleNames=Business',
                 text='', status_code=403)
    success = pentaho.roles.remove_from_user('test', ['Business'])
    assert not success


def test_role_api_remove_fail_2(pentaho=pentaho()):
    with pytest.raises(ValueError):
        pentaho.roles.remove_from_user('test', 'Business')


@requests_mock.Mocker(kw='mock_api')
def test_role_api_create_role_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/createRole?roleName=test', text='')
    success = pentaho.roles.create('test')
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_role_api_create_role_fail(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/createRole?roleName=test', text='', status_code=403)
    success = pentaho.roles.create('test')
    assert not success


@requests_mock.Mocker(kw='mock_api')
def test_role_api_delete_roles_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/deleteRoles?roleNames=test', text='')
    success = pentaho.roles.delete('test')
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_role_api_delete_roles_list_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/deleteRoles?roleNames=test1%09test2', text='')
    success = pentaho.roles.delete(['test1', 'test2'])
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_role_api_delete_roles_fail(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/deleteRoles?roleNames=test', text='', status_code=403)
    success = pentaho.roles.delete('test')
    assert not success


@requests_mock.Mocker(kw='mock_api')
def test_role_api_list_success(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/roles', text=list_roles())
    roles_list = pentaho.roles.list()
    assert len(roles_list) == 3


@requests_mock.Mocker(kw='mock_api')
def test_role_api_list_fail(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/roles', text='', status_code=500)
    roles_list = pentaho.roles.list()
    assert len(roles_list) == 0


@requests_mock.Mocker(kw='mock_api')
def test_role_api_list_user_success(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/roleMembers?roleName=test', text=list_users())
    user_list = pentaho.roles.list_members('test')
    assert len(user_list) == 6


@requests_mock.Mocker(kw='mock_api')
def test_role_api_list_user_fail(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/roleMembers?roleName=test', text='', status_code=500)
    user_list = pentaho.roles.list_members('test')
    assert len(user_list) == 0


@requests_mock.Mocker(kw='mock_api')
def test_role_api_assign_perm_success(mock_api, pentaho=pentaho()):
    mock_api.put('http://test.com/pentaho/api/userroledao/roleAssignments', text='')
    success = pentaho.roles.assign_permissions_to_role('test1', read=True, create=True)
    assert success


@requests_mock.Mocker(kw='mock_api')
def test_role_api_list_perm_role_map_success(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/logicalRoleMap?locale=en', text=list_perm_role_map())
    perm_role_map = pentaho.roles.get_permissions_role_map()
    assert len(perm_role_map['assignments']) == 2
    assert len(perm_role_map['localizedRoleNames']) == 7


@requests_mock.Mocker(kw='mock_api')
def test_role_api_list_perm_role_map_fail(mock_api, pentaho=pentaho()):
    mock_api.get('http://test.com/pentaho/api/userroledao/logicalRoleMap?locale=en', text='', status_code=403)
    perm_role_map = pentaho.roles.get_permissions_role_map()
    assert not perm_role_map
