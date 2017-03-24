# -*- coding: utf-8 -*-
"""The base command class, with shared options from all other commands."""


import ConfigParser
import logging
import ldap


class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

        # load logging
        self.log = logging.getLogger("")

        # load configuration
        self.conf = ConfigParser.ConfigParser()
        self.conf.optionxform = str
        try:
            self.conf.read(self.options['--config'])
        except:
            self.log.warning(
                "Missing configuration from %s." % options['--config'])
            self.log.warning("Loading defaults from default-config.cfg.")
            try:
                self.conf.read('default-config.cfg')
            except:
                self.log.critical(
                   "Could not load configuration defaults. Exiting.")
                exit(1)

        # load ldap server
        ldap_server = "%s:%d" % (
            self._get_config_str('Main', 'LDAP_HOST'),
            self._get_config_int('Main', 'LDAP_PORT'))

        self.log.debug("Initializing LDAP Server %s" % ldap_server)
        try:
            self.ldap = ldap.initialize(ldap_server)
            self.ldap_scope = ldap.SCOPE_SUBTREE
        except ldap.LDAPError as e:
            self.log.critical(
                "Error initializing LDAP Server: %s" % e['desc'])
            exit(1)

        if (self._get_config_bool('Main', 'LDAP_TLS')):
            try:
                self.ldap.start_tls_s()
            except Exception as e:
                self.log.critical(
                    "Could not start TLS with the LDAP Server: %s." % e)
                exit(1)

        ldap_bind_dn = self._get_config_str('Main', 'LDAP_BIND_DN')
        ldap_bind_pw = self._get_config_str('Main', 'LDAP_BIND_PW')
        self.log.debug("Binding to the LDAP Server with '%s'." % ldap_bind_dn)
        try:
            self.ldap.simple_bind_s(ldap_bind_dn, ldap_bind_pw)
        except Exception as e:
            self.log.critical(
                "Error binding to LDAP Server: %s" % e)
            exit(1)

        # setup email configuration
        self.smtp = {}
        self.smtp['smtp_host'] = self._get_config_str(
            'Email', 'EMAIL_SMTP_HOST')
        self.smtp['smtp_port'] = self._get_config_int(
            'Email', 'EMAIL_SMTP_PORT')
        self.smtp['smtp_tls'] = self._get_config_bool(
            'Email', 'EMAIL_SMTP_TLS')
        self.smtp['smtp_auth'] = self._get_config_bool(
            'Email', 'EMAIL_SMTP_AUTH')
        self.smtp['smtp_user'] = self._get_config_str(
            'Email', 'EMAIL_SMTP_USER')
        self.smtp['smtp_pass'] = self._get_config_str(
            'Email', 'EMAIL_SMTP_PASS')

    def _get_config_bool(self, section, option):
        return self.conf.getboolean(section, option)

    def _get_config_int(self, section, option):
        return self.conf.getint(section, option)

    def _get_config_float(self, section, option):
        return self.conf.getfloat(section, option)

    def _get_config_str(self, section, option):
        return self.conf.get(section, option)

    def _get_config_items(self, section):
        return self.conf.items(section)

    def _get_config_all(self):
        list = []
        for s in self.conf.sections():
            new_list = self._get_config_items(s)
            list = list + new_list
        return list

    def permission_denied(self, e):
        self.log.error("Permission denied.")
        exit(2)

    def run(self):
        raise NotImplementedError(
            'You must implement the run() method yourself!')
