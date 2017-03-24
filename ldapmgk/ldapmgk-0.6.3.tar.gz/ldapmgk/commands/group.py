# -*- coding: utf-8 -*-
"""The group command class."""

from .base import Base
import ldap
import ldap.modlist as modlist
import pprint


class Group(Base):

    def run(self):
        try:
            action = self.options['ACTION'].lower()
        except:
            self.log.critical(
                "ldapmgk group: invalid action. It must be a string.")
            exit(1)

        groupname = self.options['<groupname>']

        if (self.options['<username>']):
            username = self.options['<username>']
        else:
            username = None

        if (action == 'list'):
            self.list_groups(echo=True)
        elif (action == 'show'):
            self.search(groupname, echo=True)
        elif (action == 'create'):
            if (self.add_group(groupname)):
                self.log.info("Sucessfully added group %s." % groupname)
            else:
                exit(1)

        elif (action == 'delete'):
            if (self.delete_group(groupname)):
                self.log.info("Sucessfully removed group %s." % groupname)
            else:
                exit(1)

        elif (action == 'add'):
            if (self.add_user_to_group(username, groupname)):
                self.log.info(
                    "Sucessfully added user %s to group %s." % (
                        username,
                        groupname,
                    ))
            else:
                exit(1)

        elif (action == 'remove'):
            if (self.remove_user_from_group(username, groupname)):
                self.log.info(
                    "Sucessfully removed user %s from group %s." % (
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
        self.log.debug("Searching for group.")
        group_filter = self._get_config_str('Main', 'LDAP_GROUP_FILTER')
        group_dn = self._get_config_str('Main', 'LDAP_GROUP_DN')
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
                print "Group %s not found." % groupname

            return False

    def list_groups(self, echo=False):
        group_filter = self._get_config_str('Main', 'LDAP_GROUP_FILTER')
        group_dn = self._get_config_str('Main', 'LDAP_GROUP_DN')
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
            print "Groups:"
            rs.sort(key=lambda i: i[1])
            for k, v in rs:
                print "  %s" % v[group_filter][0]
        else:
            return rs

    def add_group(self, groupname, description=None):
        group_dn = self.search(groupname)

        self.log.debug(
            "Adding group %s" % groupname)

        if (group_dn):
            self.log.warning("Group already exists. Nothing to do.")
            exit(1)
        else:
            groups_dn = self._get_config_str('Main', 'LDAP_GROUP_DN')
            group_dn = "cn=%s,%s" % (groupname, groups_dn)

        object_classes = self._get_config_str('Main', 'LDAP_GROUP_ATTRS')
        object_classes = object_classes.split(',')

        if not description:
            description = ''

        base_dn = self._get_config_str('Main', 'LDAP_BASE_DN')

        add_record = {
            'objectClass': object_classes,
            'cn': groupname,
            'description': description,
            'member': "cn=manager,%s" % base_dn
        }

        ldif = modlist.addModlist(add_record)

        try:
            self.ldap.add_s(group_dn, ldif)
        except ldap.LDAPError as e:
            self.log.error(
                "Error while adding group %s: %s" % (groupname, e))
            return False

        return True

    def delete_group(self, groupname):
        group_dn = self.search(groupname)

        self.log.debug(
            "Removing group %s" % groupname)

        if not (group_dn):
            self.log.warning("Group doesn't exist. Nothing to do.")
            exit(1)

        try:
            self.ldap.delete_s(group_dn)
        except ldap.LDAPError as e:
            self.log.error(
                "Error while removing group %s: %s" % (groupname, e))
            return False

        return True

    def add_user_to_group(self, username, groupname):
        group_dn = self.search(groupname)
        users_dn = self._get_config_str('Main', 'LDAP_USER_DN')
        user_dn = "cn=%s,%s" % (username, users_dn)

        if not (group_dn):
            self.log.warning("Group doesn't exist. Nothing to do.")
            exit(1)

        try:
            self.ldap.modify_s(
                group_dn,
                [(ldap.MOD_ADD, 'member', user_dn)]
            )
        except ldap.LDAPError as e:
            self.log.error(
                "Error while adding user %s to group %s: %s" % (
                    username,
                    groupname,
                    e))
            return False

        return True

    def remove_user_from_group(self, username, groupname):
        group_dn = self.search(groupname)
        users_dn = self._get_config_str('Main', 'LDAP_USER_DN')
        user_dn = "cn=%s,%s" % (username, users_dn)

        if not (group_dn):
            self.log.warning("Group doesn't exist. Nothing to do.")
            exit(1)

        try:
            self.ldap.modify_s(
                group_dn,
                [(ldap.MOD_DELETE, 'member', user_dn)]
            )
        except ldap.LDAPError as e:
            self.log.error(
                "Error while removing user %s from group %s: %s" % (
                    username,
                    groupname,
                    e))
            return False

        return True
