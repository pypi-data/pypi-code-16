#!/usr/bin/env python
from __future__ import print_function, division, unicode_literals, absolute_import
# from future.utils import with_metaclass

import logging
from actappliance.act_errors import act_errors, ACTError
from actappliance.permissions import AppliancePermissions
from actappliance.connection import ApplianceSsh, ApplianceRest


class Appliance(object):
    """
    An appliance represents CDS or SKY actifio product.

    As a general rule use cmd method for all udsinfo and udstask commands. This allows them to be changed dynamically
    at runtime. If you are sending a hidden rest command use rest and if you are sending a command that can't be sent
    over rest use raw.

    Usage:
     a = Appliance(ip_address='172.27.4.0'
     r = a.cmd('udsinfo lshost -filtervalue hostname=dog&hosttype=puppey')
     hostid = r.parse(k='id')

    Commands themselves should go into Libraries not this class.
    """

    def __init__(self, hostname=None, ip_address=None, connection_type='rest', appliance_type=None, ssh_args=None,
                 rest_params=None):
        """
        Setup config info as well as permissions

        ssh_args should normally have username, password, port as keys.
        rest_params should normally have name, password, vendorkey as keys.

        :param hostname: DNS name of machine to connect to (hostname or ip_address required)
        :param ip_address: Ip address of machine to connect to (hostname or ip_address required)
        :param connection_type: Default way to connect to appliance (options: cli, rest)
        :param appliance_type: Category of appliance
        :param ssh_args: Dictionary of ssh connection args to send to paramiko's connect method
        :param rest_params: Dictionary of connection params to send alongside RESTful requests
        """
        # These permissions are to stop users from hitting unexpected failures. Not for security.
        self.perms = AppliancePermissions()

        self.logger = logging.getLogger(__name__)

        # Get system info
        self.hostname = hostname
        self.ip_address = ip_address
        self.system = ip_address or hostname
        if not self.system:
            self.logger.warn('Ip address or hostname required to send commands')

        # Get connection info
        self.ssh_args = ssh_args if ssh_args is not None else {}
        self.rest_params = rest_params if rest_params is not None else {}

        # Get optional appliance type
        self.appliance_type = appliance_type.lower() if appliance_type is not None else None

        # Ensure connection input is valid
        connection_type = connection_type.lower()
        if connection_type in ('rest', 'cli'):
            self.connection_type = connection_type
        else:
            raise ValueError("connection_type accepts 'rest' or 'cli'; {} was given".format(connection_type))

        # Make connections for commands
        self._make_connections()

    def _make_connections(self):
        self.rest_conn = ApplianceRest(self.system, params=self.rest_params)
        self.ssh_conn = ApplianceSsh(self.system, **self.ssh_args)

    def cmd(self, operation, **update_cmds):
        """
        Connect to the machine using the classes connection type and send the given command.

        If an argument needs to be sent in the operation and not in kwargs with argument make sure it is first in the
        series of commands.

        :param operation: CLI-like command to send
        :param update_cmds: add or overwrite commands in the operation. Will not add if value is none.
        :return: ActResponse object
        """
        self.perms.has_cmd()
        if self.connection_type == "rest":
            return self.rest(operation, **update_cmds)
        elif self.connection_type == "cli":
            return self.cli(operation, **update_cmds)
        else:
            raise RuntimeError("Couldn't find suitable cmd method based on connection type. {} "
                               "provided".format(self.connection_type))

    def rest(self, operation, **update_cmds):
        """
        Use when you explicitly want to connect over RESTful API.

        :param operation: CLI-like command to be sent. ex. udsinfo lshost
        :param update_cmds: keyword arguments to be sent with command
        :return:
        """
        self.perms.has_rest()

        return self.rest_conn.cmd(operation, **update_cmds)

    def cli(self, operation, **update_cmds):
        """
        Use when you explicitly want to connect over ssh.

        :param operation: CLI-like command to be sent. ex. udsinfo lshost
        :param update_cmds: keyword arguments to be sent with command
        :return: ActResponse object
        """
        self.perms.has_ssh()

        return self.ssh_conn.cmd(operation, **update_cmds)

    def raw(self, command):
        """
        Use when you explicitly want to connect over ssh and send raw ssh commands.

        This houses the functionality unlike rest method because I want to avoid passing around the client to retain
        channels.
        :param command:
        :return: stdout, stderr, exit status
        """
        self.perms.has_ssh()

        return self.ssh_conn.raw(command)

    def ui_call(self, method, url_suffix, params=None, data=None, **kwargs):
        """
        Used to send Actifio desktop rest calls.

        :param method: type of rest call to make. ie. GET, POST
        :param input_dictionary: python object to be converted to json
        :param url_suffix: What follows actifio in the UI call. i.e. https://<some_hostname>/actifio/<url_suffix here>
        :return:
        """
        self.perms.has_rest()
        return self.rest_conn.ui_call(method, url_suffix, params, data, **kwargs)

    def teardown(self):
        self.rest_conn.disconnect()
        self.ssh_conn.disconnect()

    def get_appliance_type(self):
        """
        Checks if current appliance is CDS or Sky.

        :return: cds or sky as string
        """
        from paramiko import AuthenticationException

        appliance_type = None

        try:
            self.logger.debug("Searching for appliance type over ssh.")
            out, err, rc = self.ssh_conn.raw('rpm -qa | grep actsys | grep -ho -e svc -e sky')
            actsys_type = out[0].lower()
            appliance_type = actsys_type.replace('svc', 'cds')

            assert appliance_type == 'cds' or appliance_type == 'sky', "Appliance type found from rpm -qa isn't sky " \
                                                                       "or svc"
        except AuthenticationException:
            self.logger.debug("Failed to get appliance type over ssh, searching with RESTful API.")
            r = self.rest('udsinfo lsversion')
            for di in r['result']:
                appliance_type = 'sky' if 'Sky' in di.itervalues() else 'cds' if 'CDS' in di.itervalues() else None
                if appliance_type:
                    break

        assert appliance_type == 'cds' or appliance_type == 'sky', "Invalid appliance type {0}" \
                                                                   "found".format(appliance_type)
        self.logger.info("Successfully got appliance type {}.".format(appliance_type))
        self.appliance_type = str(appliance_type)

    def new_user(self, new_name, new_password=None):
        """
        This is an idempotent way to select and sign in as a new user with default rights.

        :param new_name: New username to create or find
        :param new_password: New password to set or use
        """
        if new_password is None:
            new_password = self.rest_params.get('password')

        # we don't need to check_login if exceptions aren't hit
        check_login = False
        try:
            r = self.cmd('udstask mkuser', name=new_name, password=new_password)
            r.raise_for_error()
        except act_errors[10006]:
            # This assumes the password of the created user is new_password
            logging.info('User {} already existed.'.format(new_name))
            # Check the password we have works
            check_login = True
        finally:
            self.teardown()

        # Remove the ssh permissions
        self.perms.ssh = False
        # set the new params
        self.rest_params['name'] = new_name
        self.rest_params['password'] = new_password
        self._make_connections()

        # If we found an existing user, make sure our password works
        if check_login:
            r = self.rest('udsinfo lsversion')
            try:
                r.raise_for_error()
            except ACTError:
                raise RuntimeError("User {} already existed and the provided password was incorrect.".format(new_name))
