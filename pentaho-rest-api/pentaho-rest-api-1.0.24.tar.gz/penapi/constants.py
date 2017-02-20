# Pentaho endpoint constants


#############################################
# User Endpoint
#############################################

PENTAHO_USERS_ENDPOINT_API = "users"

USERS_USERNAME_VAR = "userName"
USERS_PASSWORD_VAR = "password"

USERS_NEW_PASSWORD_VAR = "newPassword"
USERS_OLD_PASSWORD_VAR = "oldPassword"
USERS_DELETE_VAR = "userNames"

ROLE_CREATE_VAR = "roleName"
ROLE_DELETE_VAR = "roleNames"
ROLE_LIST_MEMBERS_VAR = "roleName"
ROLE_MAP_LOCALE_VAR = "locale"

LIST_USERS = "list_users"
CREATE_USERS = "create_users"
DELETE_USERS = "delete_users"
CHANGE_USER_PASSWORD = "change_user_password"

TAB_SEPARATOR = '\t'

# see documentation here https://help.pentaho.com/Documentation/6.0/0R0/070/010/0D0/0O0
PENTAHO_USER_ENDPOINT_DEFINITION = {
    CREATE_USERS: ("put", "/pentaho/api/userroledao/createUser"),
    LIST_USERS: ("get", "/pentaho/api/userroledao/users"),
    DELETE_USERS: ("put", "/pentaho/api/userroledao/deleteUsers"),
    CHANGE_USER_PASSWORD: ("put", "/pentaho/api/userroledao/user")
}

#############################################
# Role Endpoint
#############################################

PENTAHO_ROLES_ENDPOINT_API = "roles"

ROLES_ASSIGN_VAR = "roleNames"

GET_ROLES_FOR_USER = "list_user_roles"
ASSIGN_ROLE_TO_USER = "assign_role_to_user"
REMOVE_ROLE_FROM_USER = "remove_role_from_user"
CREATE_ROLE = "create_role"
DELETE_ROLE = "delete_role"
LIST_ROLES = "list_roles"
LIST_MEMBERS_ROLE = "list_members_role"
ASSIGN_PERM_TO_ROLE = "assign_perm_to_role"
LIST_PERM_ROLE_MAP = "perm_role_map"

PENTAHO_ROLE_ENDPOINT_DEFINITION = {
    GET_ROLES_FOR_USER: ("get", "/pentaho/api/userroledao/userRoles"),
    ASSIGN_ROLE_TO_USER: ("put", "/pentaho/api/userroledao/assignRoleToUser"),
    REMOVE_ROLE_FROM_USER: ("put", "/pentaho/api/userroledao/removeRoleFromUser"),
    CREATE_ROLE: ("put", "/pentaho/api/userroledao/createRole"),
    DELETE_ROLE: ("put", "/pentaho/api/userroledao/deleteRoles"),
    LIST_ROLES: ("get", "/pentaho/api/userroledao/roles"),
    LIST_MEMBERS_ROLE: ("get", "/pentaho/api/userroledao/roleMembers"),
    ASSIGN_PERM_TO_ROLE: ("put", "/pentaho/api/userroledao/roleAssignments"),
    LIST_PERM_ROLE_MAP: ("get", "/pentaho/api/userroledao/logicalRoleMap")
}

#############################################
# Files Endpoint
#############################################

PENTAHO_FILES_ENDPOINT_API = "files"

CREATE_DIRECTORY = "create_directory"
LIST_DIRECTORY = "list_directory"
GET_ACL = "get_acl"
SET_ACL = "set_acl"

PENTAHO_FILE_ENDPOINT_DEFINITION = {
    CREATE_DIRECTORY: ("put", "/pentaho/api/repo/dirs/"),
    LIST_DIRECTORY: ("get", "/pentaho/api/repo/files/"),
    GET_ACL: ("get", "/pentaho/api/repo/files/"),
    SET_ACL: ("put", "/pentaho/api/repo/files/")
}

#############################################
# Pentaho class constant
#############################################

PENTAHO_BASIC_AUTH = 'basic'
PENTAHO_COOKIE_AUTH = 'cookie'
PENTAHO_DEFAULT_COOKIE_NAME = 'JSESSIONID'

PENTAHO_AVAILABLE_ENDPOINT_TYPE = {
    PENTAHO_USERS_ENDPOINT_API: PENTAHO_USER_ENDPOINT_DEFINITION,
    PENTAHO_ROLES_ENDPOINT_API: PENTAHO_ROLE_ENDPOINT_DEFINITION,
    PENTAHO_FILES_ENDPOINT_API: PENTAHO_FILE_ENDPOINT_DEFINITION
}
