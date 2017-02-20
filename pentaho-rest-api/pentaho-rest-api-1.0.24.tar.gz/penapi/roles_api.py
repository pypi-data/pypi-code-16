import logging
import re
import xmltodict

from constants import (
    TAB_SEPARATOR,
    PENTAHO_ROLES_ENDPOINT_API,
    USERS_USERNAME_VAR,
    ROLES_ASSIGN_VAR,
    ROLE_CREATE_VAR,
    ROLE_DELETE_VAR,
    ROLE_LIST_MEMBERS_VAR,
    ROLE_MAP_LOCALE_VAR,
    GET_ROLES_FOR_USER,
    ASSIGN_ROLE_TO_USER,
    REMOVE_ROLE_FROM_USER,
    CREATE_ROLE,
    DELETE_ROLE,
    LIST_ROLES,
    LIST_MEMBERS_ROLE,
    ASSIGN_PERM_TO_ROLE,
    LIST_PERM_ROLE_MAP
)

from penapi.base_api import PentahoBaseAPI

logger = logging.getLogger(__name__)


class PentahoRolesAPI(PentahoBaseAPI):

    def list_for_user(self, username):
        """
        Get roles for a user
        :param username: user to get roles
        :return: success/failure
        :rtype: list
        """
        role_list = list()
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, GET_ROLES_FOR_USER,
                                           params={USERS_USERNAME_VAR: username})
        if response.status_code == 200:
            try:
                if isinstance(xmltodict.parse(response.text)['roleList']['roles'], basestring):
                    role_list = [xmltodict.parse(response.text)['roleList']['roles']]
                else:
                    role_list = xmltodict.parse(response.text)['roleList']['roles']
            except Exception, e:
                logger.exception(e)
        return role_list

    def assign_to_user(self, username, roles):
        """
        Asign roles to a user
        :param username: user to assign roles
        :param roles: list of roles to assign to the user
        :return: success/failure
        :rtype: list
        """
        if isinstance(roles, basestring):
            raise ValueError("[ERROR] roles parameter must be iterable but not a string...")
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, ASSIGN_ROLE_TO_USER,
                                           params={USERS_USERNAME_VAR: username,
                                                   ROLES_ASSIGN_VAR: TAB_SEPARATOR.join(roles)})
        return response.status_code == 200

    def remove_from_user(self, username, roles):
        """
        Remove roles from a user
        :param username: user to assign roles
        :param roles: list of roles to remove from the user
        :return: success/failure
        :rtype: list
        """
        if isinstance(roles, basestring):
            raise ValueError("[ERROR] roles parameter must be iterable but not a string...")
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, REMOVE_ROLE_FROM_USER,
                                           params={USERS_USERNAME_VAR: username,
                                                   ROLES_ASSIGN_VAR: TAB_SEPARATOR.join(roles)})
        return response.status_code == 200

    def create(self, rolename):
        """
        Create a new role
        :param rolename: role to create
        :return: success/failure
        :rtype: boolean
        """
        if not isinstance(rolename, basestring):
            raise ValueError("[ERROR] role name parameter must be a string...")
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, CREATE_ROLE,
                                           params={ROLE_CREATE_VAR: rolename})
        return response.status_code == 200

    def delete(self, rolenames):
        """
        Delete roles in pentaho
        :param rolenames: the roles to delete (string or list)
        :return: success/failure
        :rtype: boolean
        """
        if type(rolenames) is list:
            rolenames = TAB_SEPARATOR.join(rolenames)
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, DELETE_ROLE,
                                           params={ROLE_DELETE_VAR: rolenames})
        return response.status_code == 200

    def list(self, regex=None):
        """
        Get list of all roles
        :param regex: filter pattern
        :return: list of roles
        :rtype: list
        """
        role_list = list()
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, LIST_ROLES)
        if response.status_code == 200:
            try:
                role_list = xmltodict.parse(response.text)['roleList']['roles']
            except Exception, e:
                logger.exception(e)
        if regex:
            role_list = [v for v in role_list if re.match(regex, v)]
        return role_list

    def list_members(self, rolename):
        """
        Get list of all users for this role
        :param rolename: role to list users
        :return: list of users
        :rtype: list
        """
        user_list = list()
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, LIST_MEMBERS_ROLE,
                                           params={ROLE_LIST_MEMBERS_VAR: rolename})
        if response.status_code == 200:
            try:
                user_list = xmltodict.parse(response.text)['userList']['users']
            except Exception, e:
                logger.exception(e)
        return user_list

    def assign_permissions_to_role(self, rolename, manage=False, read=False,
                                   publish=False, create=False, execute=False,
                                   manage_datasource=False,
                                   manage_security=False):
        """
        Assign permission to a role
        :param rolename: role to assign permission
        :param manage:
        :param read:
        :param publish:
        :param create:
        :param execute:
        :param manage_datasource:
        :param manage_security:
        :return: success/failure
        :rtype: boolean
        """
        logical_role_list = []
        if manage:
            logical_role_list.append("org.pentaho.scheduler.manage")
        if read:
            logical_role_list.append("org.pentaho.repository.read")
        if publish:
            logical_role_list.append("org.pentaho.security.publish")
        if create:
            logical_role_list.append("org.pentaho.repository.create")
        if execute:
            logical_role_list.append("org.pentaho.repository.execute")
        if manage_datasource:
            logical_role_list.append("org.pentaho.platform.dataaccess.datasource.security.manage")
        if manage_security:
            logical_role_list.append("org.pentaho.security.administerSecurity")

        json_payload = {
            "assignments": [
                {
                    "roleName": rolename,
                    "logicalRoles": logical_role_list
                }
            ]
        }
        if not isinstance(rolename, basestring):
            raise ValueError("[ERROR] role name parameter must be a string...")
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, ASSIGN_PERM_TO_ROLE,
                                           json=json_payload)
        return response.status_code == 200

    def get_permissions_role_map(self, locale='en'):
        """
        Get the permission role map in a dictionary format
        :param locale: locale for the permssion, 'en' by default
        :return: Dictionary of the permissions by role, or None
        """
        if not isinstance(locale, basestring):
            raise ValueError("[ERROR] locale parameter must be a string...")
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, LIST_PERM_ROLE_MAP,
                                           params={ROLE_MAP_LOCALE_VAR: locale})
        if response.status_code == 200:
            try:
                perm_role_map = xmltodict.parse(response.text)
            except Exception, e:
                return None
            return perm_role_map.get('systemRolesMap', None)
        return None
