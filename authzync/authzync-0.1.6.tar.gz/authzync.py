# -*- coding: utf-8 -*-

import ldap3
from ldap3.core import exceptions
from datetime import datetime as dt
import re
import json
import argparse
import sys
import os
import logging

__author__ = "Robert Wikman <rbw@vault13.org>"
__version__ = "0.1.6"


class GroupParseError(Exception):
    pass


class LDAPMappingError(Exception):
    pass


class LDAPQuery(ldap3.Connection):
    """Creates a new LDAPQuery object
    Final result should be a list of a groups, each with a distinct set of members

    :param config: Authzsync config object
    """
    def __init__(self, config):
        self.config = config
        self.attr_group_members = self.config['mappings']['group_members']
        self.attr_group_name = self.config['mappings']['group_name']
        self.attr_user_name = self.config['mappings']['user_name']
        self.attr_section_name = self.config['mappings']['section_name']

        # Connect to server
        server = ldap3.Server(config['ldap']['host'], port=config['ldap']['port'], use_ssl=config['ldap']['use_ssl'])

        super(LDAPQuery, self).__init__(server,
                                        return_empty_attributes=True,
                                        raise_exceptions=True,
                                        user=config['ldap']['bind_user'],
                                        password=config['ldap']['bind_password'])

        self.bind()

    def get_svn_groups(self):
        """Constructs a list of SVN groups from the LDAP server

        :return: list of groups
        """
        self.search(search_base=self.config['ldap']['base_dn'],
                    search_filter='(objectClass=group)',
                    search_scope=ldap3.SUBTREE,
                    attributes=[self.attr_group_name,
                                self.attr_group_members,
                                self.attr_section_name])

        groups = []

        for entry in self.entries:
            # Skip groups not matching our access_pattern
            group_match = re.match(self.config['patterns']['access_pattern'],
                                   str(entry[self.attr_group_name]),
                                   re.IGNORECASE)

            if group_match is None:
                continue

            if entry[self.attr_group_members] is not None:
                # We got a match. Make sure the expected attributes are there.
                self.__validate_group_attributes(entry)
                groups.append({
                    'name': entry[self.attr_group_name][0],
                    'section': entry[self.attr_section_name][0],
                    'members': self._get_members(entry[self.attr_group_members])
                })

        return groups

    def __validate_group_attributes(self, result):
        """Makes sure the expected attributes exists in a successful search result

        :param result: result to compare
        :raises:
            :LDAPMappingError: If there's a mapping missing
        """
        for attr in [self.attr_group_name, self.attr_section_name, self.attr_group_members]:
            if attr not in result:
                raise LDAPMappingError("Property '%s' not found in result. "
                                       "Please check your mappings" % attr)

    def _get_member(self, dn):
        """Gets information about an LDAP user object

        :param dn: User DN string
        :return: ldap3 search result
        """
        self.search(search_base=dn,
                    search_filter='(objectClass=*)',
                    search_scope=ldap3.SUBTREE,
                    attributes=[self.attr_group_name,
                                self.attr_user_name,
                                self.attr_group_members])

        return self.entries

    def _get_members(self, dn):
        """Takes DN's and returns a list of resolved user objects

        :param dn: str() or list() of user DN's
        :return: set() of user UID's
        """
        members = []

        for member in map(self._get_member, dn):
            m = member[0]
            if len(m[self.attr_group_members]) > 0:  # check if nested
                # Call _get_members() recursively with a list of member DN's
                members.extend(self._get_members(m[self.attr_group_members]))
            else:
                members.append(m[self.attr_user_name][0])

        return set(members)


class Authz(object):
    """Creates a new Authz object for writing to the SVN access file

    :param file: svn authz file
    :param config: authzync configuration dict
    :param local_db_file: Local user authz config
    """
    def __init__(self, file, config, local_db_file):
        self.logger = logging.getLogger(__name__)
        self.file = file
        self.config = config
        self.local_db_file = local_db_file
        self.repositories = {}

        self.user_count = 0

    def push_repository(self, name, path, access, members):
        """Builds repository configuration dict, later used to generate the authz configuration file

        :param name: repository name
        :param path: repository path (i.e. /branches/test
        :param access: permissions (RO/RW)
        :param members: users allowed to access the repo
        """
        if name not in self.repositories:
            self.repositories.update({name: {}})

        if path not in self.repositories[name]:
            self.repositories[name].update(
                {
                    path: {
                        'RO': [],
                        'RW': []
                    }
                }
            )

        if members:
            self.repositories[name][path][access].extend(members)
            self.user_count += len(members)

    def write(self):
        """ Writes header and contents from `Group`

        """
        fh = open(self.file, 'w')
        fh.write("\n## AUTOMATICALLY GENERATED FILE - DO NOT EDIT ##")
        fh.write("\n##")
        fh.write("\n## Generated by: %s" % sys.argv[0])
        fh.write("\n## Generated at: %s" % dt.now())
        fh.write("\n## Sources used:")
        fh.write("\n##   - Local: %s" % self.local_db_file)
        fh.write("\n##   - LDAP: %s (%s)" % (self.config['ldap']['host'], self.config['ldap']['base_dn']))
        fh.write("\n##")
        fh.write("\n## Visit https://github.com/rbw0/authzync for more info\n")

        for repo_name in self.repositories:
            sections = self.repositories[repo_name]
            for path in sections:
                fh.write("\n[%s:%s]\n" % (repo_name, path))

                if sections[path]['RO']:
                    fh.write(''.join('%s = r\n' % t for t in sections[path]['RO']))

                if sections[path]['RW']:
                    fh.write(''.join('%s = rw\n' % t for t in sections[path]['RW']))

        fh.write("\n")
        fh.close()

        return os.stat(self.file).st_size


class Group(object):
    """Creates a new group object by parsing results from LDAP or local_db file

    :param name_raw: Group name (str) to match and parse according to `access_pattern`
    :param section_raw: Section / full SVN path to match and parse according to to `section_pattern`
    :param members: list() of group members to parse
    :param config: Authzync configuration object
    """
    def __init__(self, name_raw, section_raw, members, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.members_raw = members
        self.group_name_raw = str(name_raw)
        self.section_path_raw = str(section_raw)

        self.m_access = re.match(self.config['patterns']['access_pattern'], self.group_name_raw, re.IGNORECASE)
        self.m_section = re.match(self.config['patterns']['section_pattern'], self.section_path_raw)

    @property
    def name(self):
        """ `name` setter

        :raises: Raises GroupParseError if unable to parse repo name
        """
        try:
            return self.m_section.group('repo_name')
        except (IndexError, AttributeError):
            raise GroupParseError("Couldn't parse repository name in attribute '%s' "
                                  "(%s) for group '%s'. Pattern: %s" % (
                                      self.config['mappings']['section_name'],
                                      self.section_path_raw, self.group_name_raw,
                                      self.config['patterns']['section_pattern'])
                                  )

    @property
    def repo_access(self):
        """ `access` setter

        :raises: GroupParseError if unable to parse repo access level
        """
        try:
            return self.m_access.group('repo_access').upper()
        except (IndexError, AttributeError):
            raise GroupParseError("Couldn't get repository permission from group "
                                  "'%s', using nocase pattern: %s" % (
                                    self.group_name_raw,
                                    self.config['patterns']['access_pattern'])
                                  )

    @property
    def repo_path(self):
        """ `path` setter

        :raises: GroupParseError if unable to parse repo path
        """
        try:
            return self.m_section.group('repo_path')
        except (IndexError, AttributeError):
            raise GroupParseError("Couldn't parse repository path in attribute '%s' "
                                  "(%s) for group '%s'. Pattern: %s" % (
                                      self.config['mappings']['section_name'],
                                      self.section_path_raw, self.group_name_raw,
                                      self.config['patterns']['section_pattern'])
                                  )

    @property
    def members(self):
        """ `members` setter
        Sets members property to a `list` of users
        Silently catches and skips repo groups without members
        """
        if isinstance(self.members_raw, ldap3.abstract.attribute.Attribute):
            try:
                return [str(user.name) for user in self.members_raw]
            except exceptions.LDAPKeyError:
                self.logger.warning("No members (LDAP) found for repository '%s'" % self.name)
                pass

        return self.members_raw


def create_logger(config, stdout_enabled):
    """Creates a logger used throughout the application

    :return: logger instance
    """
    logger = logging.getLogger(__name__)

    if not stdout_enabled:
        h = logging.FileHandler(config['logging']['file'])
    else:
        h = logging.StreamHandler()

    if config['logging']['debug'] is True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    formatter = logging.Formatter(config['logging']['format'])
    h.setFormatter(formatter)
    logger.addHandler(h)

    return logger


def main():
    # Argument parser
    parser = argparse.ArgumentParser(description='SVN AuthZ-LDAP sync tool')
    parser.add_argument('--config', dest="config_file", required=True, help='configuration file')
    parser.add_argument('--authz', dest="authz_file", required=True, help='SVN authz file')
    parser.add_argument('--local_db', dest="local_db_file", required=False, help='local users / groups')
    parser.add_argument('--log_stdout', dest="stdout_enabled", action='store_true', help='enables logging to stdout')
    args = parser.parse_args()

    # Read config
    with open(args.config_file) as config_file:
        config = json.load(config_file)

    # Create logger
    logger = create_logger(config, args.stdout_enabled)
    logger.info('### SVN Authz-LDAP sync starting ###')

    # Create authz instance
    authz = Authz(file=args.authz_file, config=config, local_db_file=args.local_db_file)

    # Check if local_db_file was passed as an argument, and if so, `add` its config to `authz`
    if args.local_db_file:
        with open(args.local_db_file) as local_db_file:
            local_db = json.load(local_db_file)
            logger.info("Getting local repository data")
            for g in [Group(entry['name'], entry['section'], entry['members'], config) for entry in local_db]:
                try:
                    logger.debug("Pushing into repository: %s (%s), "
                                 "members: %s" % (g.name, g.group_name_raw, g.members))
                    authz.push_repository(g.name, g.repo_path, g.repo_access, g.members)
                except GroupParseError as e:
                    logger.error(e)

    try:
        l = LDAPQuery(config)
    except (exceptions.LDAPSocketOpenError,
            exceptions.LDAPSocketReceiveError,
            exceptions.LDAPInvalidCredentialsResult) as e:
        logger.critical(e)
        sys.exit(1)

    try:
        logger.info("Getting LDAP repository data")
        groups = [Group(group['name'], group['section'], group['members'], config) for group in l.get_svn_groups()]
    except (exceptions.LDAPNoSuchObjectResult,
            LDAPMappingError) as e:
        logger.critical(e)
        sys.exit(1)
    except KeyError:
        logger.critical("Error decoding response from server. "
                        "Make sure base DN(%s) and mappings are properly configured."
                        % config['ldap']['base_dn'])
        sys.exit(1)
    finally:
        l.unbind()

    # Iterate over `Group` instances and add them to Authz
    for g in groups:
        try:
            logger.debug("Pushing into repository: %s (%s), "
                         "members: %s" % (g.name, g.group_name_raw, g.members))
            authz.push_repository(g.name, g.repo_path, g.repo_access, g.members)
        except GroupParseError as e:
            logger.error(e)

    logger.info("Loaded %d user entries in %d repositories" % (authz.user_count, len(authz.repositories)))

    if not authz.repositories:
        logger.critical("No valid authz rules found. Bailing out...")
        sys.exit(1)

    size = authz.write()
    logger.info("Wrote %d bytes to authz file: %s" % (size, args.authz_file))

if __name__ == "__main__":
    main()
