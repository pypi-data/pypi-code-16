import pymysql
import os

table_create_stmt = """
create schema if not exists _MysqlRoles;
use _MysqlRoles;

create table if not exists log_action (
  `client` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `host` char(60)COLLATE utf8_bin NOT NULL DEFAULT '',
  `time` timestamp default CURRENT_TIMESTAMP,
  `content` LONGTEXT,
  PRIMARY KEY (`time`));

CREATE TABLE IF NOT EXISTS user (
  `FromHost` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `UserName` char(16) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Plugin` char(64) COLLATE utf8_bin DEFAULT '',
  `Authentication_String` text COLLATE utf8_bin,
  PRIMARY KEY (`UserName`));

CREATE TABLE IF NOT EXISTS host (
  `Name` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Address` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Comments` text COLLATE utf8_bin,
  PRIMARY KEY (`Name`));

CREATE TABLE IF NOT EXISTS user_group (
  `Name` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Description` text COLLATE utf8_bin,
  PRIMARY KEY (`Name`));

CREATE TABLE IF NOT EXISTS host_group (
  `Name` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Description` text COLLATE utf8_bin,
  PRIMARY KEY (`Name`));

CREATE TABLE IF NOT EXISTS host_group_membership (
  `HostName` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `GroupName` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`HostName`,`GroupName`),
  FOREIGN KEY (`HostName`) REFERENCES host(Name),
  FOREIGN KEY (`GroupName`) REFERENCES host_group(Name));

CREATE TABLE IF NOT EXISTS user_group_membership (
  `UserName` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `GroupName` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`UserName`,`GroupName`),
  FOREIGN KEY (`UserName`) REFERENCES user(UserName),
  FOREIGN KEY (`GroupName`) REFERENCES user_group(Name));

CREATE TABLE IF NOT EXISTS permission_type (
  `Name` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Select_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Insert_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Update_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Delete_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Drop_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Reload_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Shutdown_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Process_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `File_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Grant_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `References_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Index_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Show_db_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Super_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_tmp_table_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Lock_tables_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Execute_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Repl_slave_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Repl_client_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Show_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_user_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Event_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Trigger_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_tablespace_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  PRIMARY KEY (`Name`));

CREATE TABLE IF NOT EXISTS access(
  `Name` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `UserGroup` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `HostGroup` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `PermissionType` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Schema` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`Name`),
  index `relation_idx` (`UserGroup`,`HostGroup`,`PermissionType`),
  FOREIGN KEY (`UserGroup`) REFERENCES user_group(Name),
  FOREIGN KEY (`HostGroup`) REFERENCES host_group(Name),
  FOREIGN KEY (`PermissionType`) REFERENCES permission_type(Name));

"""

table_seed_stmt = """
-- user creation
insert into user values ("%","Alan","mysql_native_password", password("Alan"));
insert into user values ("%","Danice","mysql_native_password", password("Danice"));
insert into user values ("%","Terry","mysql_native_password", password("Terry"));
insert into user values ("%","Rachel","mysql_native_password", password("Rachel"));
insert into user values ("%","Sam","mysql_native_password", password("Sam"));

-- db hosts
insert into host values ("report", "report", "main report host");
insert into host values ("staging", "staging", "main staging host");
insert into host values ("testing", "testing", "main testing host");
insert into host values ("cert", "cert", "main cert host");
insert into host values ("prod", "prod", "main prod host");
insert into host values ("ops", "ops", "main ops host");
insert into host values ("localhost", "127.0.0.1", "this server");

-- user groups
insert into user_group (Name) values ("Audit");
insert into user_group (Name) values ("Development");
insert into user_group (Name) values ("Testing");
insert into user_group (Name) values ("Reporting");
insert into user_group (Name) values ("Admin");

-- host groups
insert into host_group (Name) values ("all");
insert into host_group (Name) values ("dev_stack");
insert into host_group (Name) values ("preprod");
insert into host_group (Name) values ("prod");
insert into host_group (Name) values ("report");
insert into host_group (Name) values ("localhost");

-- permission types
insert into permission_type (Name, Select_priv, Show_db_priv) values ("read", "Y", "Y");
insert into permission_type (Name, Select_priv, File_priv, Show_db_priv) values ("readfile", "Y", "Y", "Y");
insert into permission_type (Name, Select_priv, Insert_priv, Update_priv, Delete_priv, Show_db_priv) values ("readwrite", "Y", "Y", "Y", "Y", "Y");
insert into permission_type (Name, Select_priv, Insert_priv, Update_priv, Delete_priv, Create_priv, Drop_priv, References_priv, Index_priv, Alter_priv, Show_db_priv) values
("schemachange", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y");
insert into permission_type (Name, Lock_tables_priv, Execute_priv, Repl_slave_priv, Repl_client_priv, Create_routine_priv, Alter_routine_priv, Create_user_priv, Event_priv, Trigger_priv, Create_tablespace_priv, Drop_priv, Show_db_priv) values
("admin", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y");
insert into permission_type values ("ALL", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y");

-- user group memberships
insert into user_group_membership values ("Alan", "Audit"), ("Danice", "Development"), ("Terry", "Testing"), ("Rachel", "Reporting"), ("Sam", "Admin");

-- insert into host groups
--  -- dev_stack
insert into host_group_membership values ("staging", "dev_stack"), ("testing", "dev_stack"), ("cert", "dev_stack"), ("prod", "dev_stack");
-- -- preprod
insert into host_group_membership values ("staging", "preprod"), ("testing", "preprod"), ("cert", "preprod");
-- -- prod
insert into host_group_membership values ("prod", "prod");
-- -- report
insert into host_group_membership values ("report", "report"), ("ops", "report");
-- -- all
insert into host_group_membership values ("report", "all"), ("staging", "all"), ("testing", "all"), ("cert", "all"), ("prod", "all"), ("ops", "all");
-- -- localhost
insert into host_group_membership values ("localhost", "localhost");


-- access grants
insert into access values ("Audit", "Audit", "all", "read", "");
insert into access values ("Development", "Development", "dev_stack", "schemachange", "");
insert into access values ("Testing", "Testing", "dev_stack", "readwrite", "");
insert into access values ("Reporting", "Reporting", "all", "readfile", "");
insert into access values ("Admin", "Admin", "all", "ALL", "");
insert into access values ("Testing_localhost", "Testing", "localhost", "readwrite", "");

"""

class RoleServ(object):

    """
    RoleServ: Server tools for MysqlRoles.
        Functions for intializing the mysql source of truth server
        and functions associated with using it.
        This class should only manage the server.

        Input:
            serv: Address of source of Truth server (default: 127.0.0.1)
    """

    @staticmethod
    def sanitize(input, allowable_list=[], default="''"):
        """
        Sanitize inputs to avoid issues with pymysql.

        Takes in an input to sanitize.
        Optionally takes in an list of allowable values and a default.
        The default is returned if the input is not in the list.
        Returns a sanizized result.
        """
        # add general sanitization
        if (input in allowable_list or allowable_list == []):
            return input
        else:
            return default

    def __init__(self, server="127.0.0.1"):
        """
        Get input and set up connection to be used with contexts (with) later.

        Standard dunder/magic method; returns nothing special.
        No special input validation.
        """
        self.server = server
        cnf_file = os.path.expanduser('~/.my.cnf')
        tmp_connection = pymysql.connect(host=self.server,
                                         autocommit=True,
                                         read_default_file=cnf_file)
        tmp_connection.cursor().execute("create schema if not exists _MysqlRoles;")
        self.connection = pymysql.connect(host=self.server,
                                          db='_MysqlRoles',
                                          autocommit=True,
                                          read_default_file=cnf_file)

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close mysql connections on destruction.

        This method may not be necessary, but is here for good practice.
        """
        self.connection.close()

    def create_tables(self):
        """
        Create tables using the table_create.sql file in the create folder.

        Returns nothing.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(table_create_stmt)

    def test_seed_tables(self):
        """
        Seed table for testing, using the seed.sql file in the create folder.

        Returns nothing.
        """
        # TODO check if tables exist first
        with self.connection.cursor() as cursor:
            cursor.execute(table_seed_stmt)

    """
    These next functions exist with the intent of use after everything has been
    set up.
    """

    def add_user(self, name, fromhost="%", plugin="mysql_native_password",
                 auth_str="*7ACE763ED393514FE0C162B93996ECD195FFC4F5"):
        """
        Add a user to the server if it does not yet exist.

        Raises a RuntimeError if the user already exists.
        Returns nothing.
        """
        name = RoleServ.sanitize(name)
        fromhost = RoleServ.sanitize(fromhost)
        plugin = RoleServ.sanitize(plugin)
        auth_str = RoleServ.sanitize(auth_str)
        # Note that the auth_str default is generated from password('changeme')
        with self.connection.cursor() as cursor:
            # check if user exists
            if cursor.execute("select (1) from user where UserName = %s",
                              (name)):
                # if so, error
                raise RuntimeError("User with username {0}\
                                   already exists.".format(name))
            # if not, add
            user_add_stmt = "insert into user values (%s, %s, %s, %s)"
            cursor.execute(user_add_stmt, (fromhost, name, plugin, auth_str))

    def add_host(self, address, name="", comments=""):
        """
        Add a host to the server if it does not yet exist.

        Raises a RuntimeError if the host already exists.
        Returns nothing.
        """
        address = RoleServ.sanitize(address)
        name = RoleServ.sanitize(name)
        comments = RoleServ.sanitize(comments)
        if name == "":
            name = address
        with self.connection.cursor() as cursor:
            # check if host exists
            if cursor.execute("select (1) from host where Name = %s",
                              (name)):
                # if so, error
                raise RuntimeError("Host with Name {0}\
                                   already exists.".format(name))
            # if not, add
            else:
                host_add_stmt = "insert into host values (%s, %s, %s)"
            cursor.execute(host_add_stmt, (name, address, comments))

    def add_host_group(self, name, description=""):
        """
        Add a host group to the server if it does not yet exist.

        Raises a RuntimeError if the host group already exists.
        Returns nothing.
        """
        name = RoleServ.sanitize(name)
        description = RoleServ.sanitize(description)
        with self.connection.cursor() as cursor:
            # check if host group exists
            if cursor.execute("select (1) from host_group where Name = %s",
                              (name)):
                # if so, error
                raise RuntimeError("Host group with Name {0}\
                                   already exists.".format(name))
            # if not, add
            hg_add_stmt = "insert into host_group values (%s, %s)"
            cursor.execute(hg_add_stmt, (name, description))

    def add_user_group(self, name, description=""):
        """
        Add a user group to the server if it does not yet exist.

        Raises a RuntimeError if the user group already exists.
        Returns nothing.
        """
        name = RoleServ.sanitize(name)
        description = RoleServ.sanitize(description)
        # Note that the auth_str default is generated from password('changeme')
        with self.connection.cursor() as cursor:
            # check if user group exists
            if cursor.execute("select (1) from user_group where Name = %s",
                              (name)):
                # if so, error
                raise RuntimeError("User group with Name {0}\
                                   already exists.".format(name))
            # if not, add
            ug_add_stmt = "insert into user_group values (%s, %s)"
            cursor.execute(ug_add_stmt, (name, description))

    def add_user_group_membership(self, username, groupname):
        """
        Add a user to a user group.

        Raises a RuntimeError if the user is already a member of the group.
        Raises a ValueError if the user does not exist.
        Raises a ValueError if the group does not exist.
        Returns nothing.
        """
        username = RoleServ.sanitize(username)
        groupname = RoleServ.sanitize(groupname)
        with self.connection.cursor() as cursor:
            # check if user exists
            if not cursor.execute("select (1) from user where UserName = %s",
                                  (username)):
                # if not, error
                raise ValueError("User with Name {0}\
                                   does not exist.".format(username))
            # check if user group exists
            if not cursor.execute("select (1) from user_group where Name = %s",
                                  (groupname)):
                # if not, error
                raise ValueError("User group with Name {0}\
                                   does not exist.".format(groupname))
            # if so, check if the membership exists already
            if cursor.execute("select (1) from user_group_membership\
                               where UserName = %s and GroupName = %s",
                              (username, groupname)):
                raise RuntimeError("{1} is already a member of\
                                   {2}".format(username, groupname))
            # if not, add it
            umem_add_stmt = "insert into user_group_membership\
                 values (%s, %s)"
            cursor.execute(umem_add_stmt, (username, groupname))

    def add_host_group_membership(self, hostname, groupname):
        """
        Add a host to a host group.

        Raises a RuntimeError if the host is already a member of the group.
        Raises a ValueError if the host does not exist.
        Raises a ValueError if the group does not exist.
        Returns nothing.
        """
        hostname = RoleServ.sanitize(hostname)
        groupname = RoleServ.sanitize(groupname)
        # Note that the auth_str default is generated from password('changeme')
        with self.connection.cursor() as cursor:
            # check if host exists
            if not cursor.execute("select (1) from host where Name = %s",
                                  (hostname)):
                # if not, error
                raise ValueError("Host with Name {0}\
                                   does not exist.".format(hostname))
            # check if host group exists
            if not cursor.execute("select (1) from host_group where Name = %s",
                                  (groupname)):
                # if not, error
                raise ValueError("Host group with Name {0}\
                                   does not exist.".format(groupname))
            # if so, check if the membership exists already
            if cursor.execute("select (1) from host_group_membership\
                               where HostName = %s and GroupName = %s",
                              (hostname, groupname)):
                raise RuntimeError("{1} is already a member of\
                                   {2}".format(hostname, groupname))
            # if not, add it
            hmem_add_stmt = "insert into host_group_membership\
             values (%s, %s)"
            cursor.execute(hmem_add_stmt, (hostname, groupname))

    def create_permission(self, name,  allgrant=False):
        """
        Create a permission type if it does not exist yet.

        Raises a RuntimeError if the permission already exists
        Does not check for duplicates.
        Returns nothing.
        """
        name = RoleServ.sanitize(name)
        # Note that the auth_str default is generated from password('changeme')
        allyes = ('"Y",'*29)[:-1]
        allno = ('"N",'*29)[:-1]
        if allgrant:
            allperm = allyes
        else:
            allperm = allno
        with self.connection.cursor() as cursor:
            # check if host group exists
            if cursor.execute("select (1) from permission_type where\
                                  Name = %s", (name)):
                # if not, error
                raise ValueError("Permission type with Name {0}\
                                   already exists.".format(name))
            ptype_add_stmt = "insert into permission_type values (%s, " + allperm + ")"
            cursor.execute(ptype_add_stmt, (name))

    def add_permission(self, name, grant, value="Y"):
        """
        Add a permission to a named permission group.
        Takes in the name of the permission to modify, which grant to perform.
        Optionally takes in a value, so that it can be used to revoke.
        grant should be a permission column name for user.
        Run for each permission desired to change

        Raises a ValueError if the permission type does not exist.
        Does not check for duplicates.
        Returns nothing.
        """
        name = RoleServ.sanitize(name)
        grant = RoleServ.sanitize(grant)
        value = RoleServ.sanitize(value, ["Y","N"], "N")
        # Note that the auth_str default is generated from password('changeme')
        with self.connection.cursor() as cursor:
            # check if permission type exists
            if not cursor.execute("select (1) from permission_type where\
                                  Name = %s", (name)):
                # if not, error
                raise ValueError("Permission type with Name {0}\
                                   does not exist.".format(name))
            perm_add_stmt = "update permission_type set " + grant + " =\
             %s where Name = %s limit 1"
            cursor.execute(perm_add_stmt, (value, name))

    def add_access(self, name, usergroup, hostgroup, permission, schema=""):
        """
        Give a user group access to a host group.

        Supports schema-level access, which defaults to empty.
        Empty Schema parameter means all schemas.
        Nonempty schema is treated like "grant (privs) on (schema) to (user)"

        Raises a RuntimeError if the the access grant exists by name.
        Raises a RuntimeError if the user access grant would be duplicated.
        Raises a ValueError if the host group does not exist.
        Raises a ValueError if the user group does not exist.
        Raises a ValueError if the permission type does not exist.
        Returns nothing.
        """
        name = RoleServ.sanitize(name)
        usergroup = RoleServ.sanitize(usergroup)
        hostgroup = RoleServ.sanitize(hostgroup)
        permission = RoleServ.sanitize(permission)
        schema = RoleServ.sanitize(schema)
        with self.connection.cursor() as cursor:
            # check if grant exists by name
            if cursor.execute("select (1) from access where Name = %s",
                              (name)):
                # if so, error
                raise RuntimeError("Access grant with Name {0}\
                                   already exists.".format(name))
            # check if grant exists by function
            if cursor.execute("select (1) from access where UserGroup = %s\
                              and HostGroup = %s",
                              (usergroup, hostgroup)):
                # if so, error
                raise RuntimeError("Access for {0} to {1} already\
                                   exists.".format(usergroup, hostgroup))
            # check if user group exists
            if not cursor.execute("select (1) from user_group where Name = %s",
                                  (usergroup)):
                # if not, error
                raise ValueError("User group with Name {0}\
                                   does not exist.".format(usergroup))
            # check if host group exists
            if not cursor.execute("select (1) from host_group where Name = %s",
                                  (hostgroup)):
                # if not, error
                raise ValueError("Host group with Name {0}\
                                   does not exist.".format(hostgroup))
            # check if permission type exists
            if not cursor.execute("select (1) from permission_type where\
                                  Name = %s",
                                  (permission)):
                # if not, error
                raise ValueError("Permission type with Name {0}\
                                   does not exist.".format(permission))
            # if all OK, add
            ag_add_stmt = "insert into access values (%s, %s, %s, %s, %s)"
            cursor.execute(ag_add_stmt, (name, usergroup, hostgroup,
                                         permission, schema))
