# -*- coding: utf-8 -*-
"""The servergroup command class."""

from .base import Base
import ldap
import pprint


class Group(Base):

    def run(self):
        try:
            action = self.options['ACTION'].lower()
        except:
            self.log.critical(
                "ldapmgk servergroup: invalid action. It must be a string.")
            exit(1)

        groupname = self.options['<groupname>']
        username = self.options['<username>']

        if (action == 'list'):
            self.list_servergroups(echo=True)
        elif (action == 'show'):
            self.search(groupname, echo=True)
        elif (action == 'add'):
            if (self.add_user_to_servergroup(username, groupname)):
                self.log.info(
                    "Sucessfully added user %s to server group %s." % (
                        username,
                        groupname,
                    ))
            else:
                exit(1)

        elif (action == 'remove'):
            if (self.remove_user_from_servergroup(username, groupname)):
                self.log.info(
                    "Sucessfully removed user %s from server group %s." % (
                        username,
                        groupname,
                    ))
            else:
                exit(1)

        else:
            self.log.critical(
                "ldapmgk group: unknown action '%s'." % action)
            exit(1)

        exit(0)

    def search(self, groupname, echo=False):
        self.log.debug("Searching for server group.")
        group_filter = self._get_config_str('Main', 'LDAP_SERVER_GROUP_FILTER')
        group_dn = self._get_config_str('Main', 'LDAP_SERVER_GROUP_DN')
        filter = "(%s=%s)" % (group_filter, groupname)

        try:
            rs = self.ldap.search_s(
                group_dn,
                self.ldap_scope,
                filter
            )
        except ldap.INSUFFICIENT_ACCESS as e:
            self.permission_denied(e)

        if len(rs) > 0:
            if (echo):
                pp = pprint.PrettyPrinter(indent=2)
                pp.pprint(rs[0][1])
            else:
                return rs[0][0]
        else:
            if (echo):
                print "Server Group %s not found." % groupname

            return False

    def list_servergroups(self, echo=False):
        group_filter = self._get_config_str('Main', 'LDAP_SERVER_GROUP_FILTER')
        group_dn = self._get_config_str('Main', 'LDAP_SERVER_GROUP_DN')
        filter = "(%s=*)" % group_filter

        try:
            rs = self.ldap.search_s(
                group_dn,
                self.ldap_scope,
                filter,
                [group_filter]
            )
        except ldap.INSUFFICIENT_ACCESS as e:
            self.permission_denied(e)

        if (echo):
            print "Server Groups:"
            rs.sort(key=lambda i: i[1])
            for k, v in rs:
                print "  %s" % v[group_filter][0]
        else:
            return rs

    def add_user_to_servergroup(self, username, groupname):
        group_dn = self.search(groupname)

        if not (group_dn):
            self.log.warning("Server group doesn't exist. Nothing to do.")
            exit(0)

        try:
            self.ldap.modify_s(
                group_dn,
                [(ldap.MOD_ADD, 'memberUid', username)]
            )
        except ldap.LDAPError as e:
            self.log.error(
                "Error while adding user %s to server group %s: %s" % (
                    username,
                    groupname,
                    e))
            return False

        return True

    def remove_user_from_servergroup(self, username, groupname):
        group_dn = self.search(groupname)

        if not (group_dn):
            self.log.warning("Group doesn't exist. Nothing to do.")
            exit(0)

        try:
            self.ldap.modify_s(
                group_dn,
                [(ldap.MOD_DELETE, 'memberUid', username)]
            )
        except ldap.LDAPError as e:
            self.log.error(
                "Error while removing user %s from server group %s: %s" % (
                    username,
                    groupname,
                    e))
            return False

        return True
