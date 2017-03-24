# -*- coding: utf-8 -*-
"""The user command class."""

import ldap
import ldap.modlist as modlist
import datetime
import pprint

from .base import Base
from ldapmgk.utils import generate_password
from ldapmgk.email import send_email


class User(Base):

    def run(self):
        # determine if using force parameter
        if (self.options['--force']):
            self.force = True
        else:
            self.force = False

        # determine if we'll send emails
        self.email_user_add = self._get_config_bool('Email', 'EMAIL_USER_ADD')
        self.email_user_resetpwd = self._get_config_bool(
             'Email', 'EMAIL_USER_RESETPWD')

        try:
            action = self.options['ACTION'].lower()
        except:
            self.log.critical(
                "ldapmgk user: invalid action. It must be a string.")
            exit(1)

        username = self.options['<username>']
        email = self.options['<email>']
        name = self.options['<name>']

        if (action == 'list'):
            self.list_users(echo=True)
        elif (action == 'show'):
            self.search(username, echo=True)
        elif (action == 'add'):
            if (name):
                name = name.split(' ')
            else:
                name = username.split('.')

            # since name is invalid, let's improvise
            if len(name) < 2:
                name = [username, username]

            password = self.add_user(username, email, name)
            if (password):
                self.log.info(
                    "Sucessfully added user %s with temporary password: %s" % (
                        username, password))
            else:
                exit(1)

        elif (action == 'remove'):
            if (self.delete_user(username)):
                self.log.info("Sucessfully removed user %s." % username)
            else:
                exit(1)

        elif (action == 'resetpwd'):
            password = self.reset_pwd(username, email)
            if (password):
                self.log.info(
                    "Sucessfully reset user %s password " % username +
                    "with temporary password: %s" % password)
            else:
                exit(1)

        else:
            self.log.critical(
                "ldapmgk user: unknown action '%s'." % action)
            exit(1)

        exit(0)

    def search(self, username, echo=False):
        self.log.debug("Searching for user.")
        user_filter = self._get_config_str('Main', 'LDAP_USER_FILTER')
        user_dn = self._get_config_str('Main', 'LDAP_USER_DN')
        filter = "(%s=%s)" % (user_filter, username)

        try:
            rs = self.ldap.search_s(
                user_dn,
                self.ldap_scope,
                filter
            )
        except ldap.INSUFFICIENT_ACCESS as e:
            self.permission_denied(e)

        # search in the inactive users tree if needed
        move_user = self._get_config_bool('Main', 'LDAP_MOVE_USER_ON_DEL')
        if (move_user):
            move_user_dn = self._get_config_str('Main', 'LDAP_MOVE_USER_DN')
            try:
                move_rs = self.ldap.search_s(
                    move_user_dn,
                    self.ldap_scope,
                    filter,
                    [user_filter]
                )
            except ldap.INSUFFICIENT_ACCESS as e:
                self.permission_denied(e)

        else:
            move_rs = None

        rs = rs + move_rs

        if len(rs) > 0:
            if (echo):
                pp = pprint.PrettyPrinter(indent=2)
                pp.pprint(rs[0][1])
            else:
                return rs[0][0]
        else:
            if (echo):
                print "User %s not found." % username

            return False

    def get_next_uid(self):
        self.log.debug("Searching for the next UID.")
        user_dn = self._get_config_str('Main', 'LDAP_USER_DN')

        try:
            rs = self.ldap.search_s(
                user_dn,
                self.ldap_scope,
                "(uidNumber=*)",
                ['uidNumber']
            )
        except ldap.INSUFFICIENT_ACCESS as e:
            self.permission_denied(e)

        # search in the inactive users tree if needed
        move_user = self._get_config_bool('Main', 'LDAP_MOVE_USER_ON_DEL')
        if (move_user):
            move_user_dn = self._get_config_str('Main', 'LDAP_MOVE_USER_DN')
            try:
                move_rs = self.ldap.search_s(
                    move_user_dn,
                    self.ldap_scope,
                    "(uidNumber=*)",
                    ['uidNumber']
                )
            except ldap.INSUFFICIENT_ACCESS as e:
                self.permission_denied(e)

            rs = rs + move_rs
        else:
            move_rs = None

        rs.sort(reverse=True, key=lambda i: i[1])
        try:
            last_uid = rs[0][1]['uidNumber'][0]
        except Exception as e:
            self.log.error("Couldn't find last UID. Error: %s" % e)

        self.log.debug("Found last UID used: %s" % last_uid)

        next_uid = int(last_uid) + 1
        self.log.debug("Returning next unused UID: %d" % next_uid)
        return next_uid

    def list_users(self, echo=False):
        user_filter = self._get_config_str('Main', 'LDAP_USER_FILTER')
        user_dn = self._get_config_str('Main', 'LDAP_USER_DN')
        filter = "(%s=*)" % user_filter

        try:
            act_rs = self.ldap.search_s(
                user_dn,
                self.ldap_scope,
                filter,
                [user_filter]
            )
        except ldap.INSUFFICIENT_ACCESS as e:
            self.permission_denied(e)

        # search in the inactive users tree if needed
        inact_user = self._get_config_bool('Main', 'LDAP_MOVE_USER_ON_DEL')
        if (inact_user):
            inact_user_dn = self._get_config_str('Main', 'LDAP_MOVE_USER_DN')
            try:
                inact_rs = self.ldap.search_s(
                    inact_user_dn,
                    self.ldap_scope,
                    filter,
                    [user_filter]
                )
            except ldap.INSUFFICIENT_ACCESS as e:
                self.permission_denied(e)

        else:
            inact_rs = None

        rs = {
            'active': act_rs,
            'inactive': inact_rs
        }

        if (echo):
            print "Active users:"
            rs['active'].sort(key=lambda i: i[1])
            for k, v in rs['active']:
                print "  %s" % v[user_filter][0]
            print

            print "Inactive users:"
            rs['inactive'].sort(key=lambda i: i[1])
            for k, v in rs['inactive']:
                print "  %s" % v[user_filter][0]
        else:
            return rs

    def add_user(self, username, email, name):

        user_dn = self.search(username)
        if (user_dn):
            self.log.warning("User already exists. Nothing to do.")
            exit(1)
        else:
            users_dn = self._get_config_str('Main', 'LDAP_USER_DN')
            user_dn = "cn=%s,%s" % (username, users_dn)

        full_name = "%s %s" % (name[0], name[1])

        self.log.debug(
            "Adding user %s (%s) - %s" % (username, email, full_name))

        object_classes = self._get_config_str('Main', 'LDAP_USER_ATTRS')
        object_classes = object_classes.split(',')

        # generate a random password
        wordlist_file = self._get_config_str(
            'Main', 'LDAP_USER_PW_RANDOM_FILE')
        with open(wordlist_file) as f:
            words = [w.strip() for w in f]
        password = generate_password(
            words,
            numbers='0123456789',
            characters='!@#$%'
        )

        add_record = {
            'objectClass': object_classes,
            'cn': username,
            'uid': username,
            'uidNumber': str(self.get_next_uid()),
            'gidNumber': '1200',
            'loginShell': '/bin/bash',
            'homeDirectory': "/home/%s" % username,
            'mail': email,
            'userPassword': password,
            'givenName': name[0],
            'sn': name[1],
            'displayName': "%s %s" % (name[0], name[1]),
        }

        ldif = modlist.addModlist(add_record)

        try:
            self.ldap.add_s(user_dn, ldif)
        except ldap.LDAPError as e:
            self.log.error(
                "Error while adding user %s: %s" % (username, e))
            return False

        # use expire rules control if needed
        expire = self._get_config_bool('Main', 'LDAP_USER_ADD_EXPIRE')
        if (expire):
            y = datetime.datetime.now() - datetime.timedelta(
                days=self._get_config_int('Main', 'LDAP_USER_ADD_EXPIRE_TIME'))
            past = y.strftime('%Y%m%d%H%M%SZ')
            serverctrls = [
                ldap.controls.simple.RelaxRulesControl()
            ]

            try:
                self.ldap.modify_ext_s(
                    user_dn,
                    [(ldap.MOD_REPLACE, 'pwdChangedTime', past)],
                    serverctrls)
            except ldap.LDAPError as e:
                self.log.error(
                     "Error while changing pwdChangedTime on user %s: %s" % (
                         username,
                         e))
                return False

        # send email if needed
        if (self.email_user_add):
            mail_from = self._get_config_str('Email', 'EMAIL_FROM')
            template_dir = self._get_config_str('Email', 'EMAIL_TEMPLATE_DIR')
            template_file = self._get_config_str('Email', 'EMAIL_TEMPLATE')
            subject = self._get_config_str('Email', 'EMAIL_SUBJECT_PREFIX')
            subject += " New access created"
            template = (template_dir, template_file)
            vars = {
                'username': username,
                'password': password
            }

            send_email(self.smtp, mail_from, email, subject, template, vars)

        return password

    def delete_user(self, username):
        user_dn = self.search(username)

        self.log.debug(
            "Removing user %s" % username)

        if not (user_dn):
            self.log.warning("User doesn't exist. Nothing to do.")
            exit(1)

        move_user = self._get_config_bool('Main', 'LDAP_MOVE_USER_ON_DEL')
        if (move_user and not self.force):
            move_user_dn = self._get_config_str('Main', 'LDAP_MOVE_USER_DN')
            new_user_dn = "cn=%s" % username
            try:
                self.ldap.rename_s(
                    user_dn,
                    new_user_dn,
                    move_user_dn,
                    True
                )
            except ldap.LDAPError as e:
                self.log.error(
                    "Error while removing (moving to inactive) user %s: %s" % (
                        username,
                        e
                    )
                )
                return False
        else:
            try:
                self.ldap.delete_s(user_dn)
            except ldap.LDAPError as e:
                self.log.error(
                    "Error while removing user %s: %s" % (username, e))
                return False

        return True

    def reset_pwd(self, username, email):

        user_dn = self.search(username)

        self.log.debug(
            "Resetting password for user %s" % username)

        if not (user_dn):
            self.log.warning("User doesn't exist. Nothing to do.")
            exit(1)

        # generate a random password
        wordlist_file = self._get_config_str(
            'Main', 'LDAP_USER_PW_RANDOM_FILE')
        with open(wordlist_file) as f:
            words = [w.strip() for w in f]
        password = generate_password(
            words,
            numbers='0123456789',
            characters='!@#$%'
        )

        try:
            self.ldap.modify_s(
                user_dn,
                [(ldap.MOD_REPLACE, 'userPassword', password)]
            )
        except ldap.LDAPError as e:
            self.log.error(
                "Error while resetting password for user %s: %s" % (
                    username,
                    e))
            return False

        # use expire rules control if needed
        expire = self._get_config_bool('Main', 'LDAP_USER_ADD_EXPIRE')
        if (expire):
            y = datetime.datetime.now() - datetime.timedelta(
                days=self._get_config_int('Main', 'LDAP_USER_ADD_EXPIRE_TIME'))
            past = y.strftime('%Y%m%d%H%M%SZ')
            serverctrls = [
                ldap.controls.simple.RelaxRulesControl()
            ]

            try:
                self.ldap.modify_ext_s(
                    user_dn,
                    [(ldap.MOD_REPLACE, 'pwdChangedTime', past)],
                    serverctrls)
            except ldap.LDAPError as e:
                self.log.error(
                     "Error while changing pwdChangedTime on user %s: %s" % (
                         username,
                         e))
                return False

        # send email if needed
        if (self.email_user_resetpwd):
            mail_from = self._get_config_str('Email', 'EMAIL_FROM')
            template_dir = self._get_config_str('Email', 'EMAIL_TEMPLATE_DIR')
            template_file = self._get_config_str('Email', 'EMAIL_TEMPLATE')
            subject = self._get_config_str('Email', 'EMAIL_SUBJECT_PREFIX')
            subject += " Password reset"
            template = (template_dir, template_file)
            vars = {
                'username': username,
                'password': password
            }

            send_email(self.smtp, mail_from, email, subject, template, vars)

        return password
