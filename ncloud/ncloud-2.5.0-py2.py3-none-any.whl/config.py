# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""
Houses configuration options and loading/saving these to disk
"""
from builtins import object, oct, str
from distutils.version import LooseVersion
import json
import logging
import os
import requests
import sys
import stat
import string
from backports import configparser

from ncloud.formatting.output import print_error
from ncloud.version import SHORT_VERSION


logger = logging.getLogger()

CMD_NAME = "ncloud"
CFG_FILE = os.path.join(os.path.expanduser("~"), "." + CMD_NAME + "rc")
CFG_DEF_HOST = "https://helium.cloud.nervanasys.com"
CFG_DEF_AUTH_HOST = "https://nervana.auth0.com"
CFG_DEF_LEGACY_AUTH_HOST = "https://auth.cloud.nervanasys.com"
CFG_DEF_AUTH0_ID = "SUCZFpKCEmTzqkb2IsTDVnnyfo5DKDPO"  # silentmigration
CFG_DEF_API_VER = "v1"
CFG_DEF_TENANT = None
CFG_SEC_DEF = "DEFAULT"
CFG_SEC_USER = "INITIAL_DETAILS"
CFG_AUTHO_CLIENT_ID_DEF = "None"

PATH = "/api/"
TOKENS = "/jwttoken/"
LEGACY_TOKENS = "/tokens/"
DATASETS = "/datasets/"
MACHINES = "/machines/"
MODELS = "/models/"
STATS = "/stats/"
MULTIPART_UPLOADS = "/multipart/"
RESOURCES = "/resources/"
BATCH_PREDICTIONS = "/predictions/batch"
STREAM_PREDICTIONS = "/predictions/stream"
AUTHENTICATION = "/oauth/ro/"
USERS = "/users/"
TENANTS = "/tenants/"
INTERACT = "/interact/"
NCLOUD_CMD_HISTORY = "/ncloud_history/"
INFO = "/info/"

NUM_THREADS = 100


# TODO rename to ConnectParams
#      allow creating with overrides in init (for test)
#      consider remove display of defaults in argparse, to reduce coupling
class Config(object):

    def __init__(self):
        self.conf = self._load_config()

    def get_selected_section(self):
        has_new_conf = False
        for section in self.conf.sections():
            if self.conf.get(section, "selected", fallback=None) == "True":
                return section
            if section == self.get_default_user_creds():
                has_new_conf = True
        return self.get_default_user_creds() if has_new_conf else \
            self.get_legacy_auth_host()

    def get_default_user_creds(self):
        return CFG_SEC_USER

    def _get_default_host(self):
        return self.conf.get(CFG_SEC_DEF, "host")

    def get_host(self):
        section = self.get_selected_section()
        return self.conf.get(section, "host", fallback=None) or \
            self._get_default_host()

    def get_tenant(self):
        section = self.get_selected_section()
        return self.conf.get(section, "tenant", fallback=None)

    def set_default_host(self, host):
        self.conf.set(CFG_SEC_DEF, "host", host)

    def get_default_auth_host(self):
        return self.conf.get(CFG_SEC_DEF, "auth_host")

    def set_default_auth_host(self, auth_host):
        self.conf.set(CFG_SEC_DEF, "auth_host", auth_host)

    def get_legacy_auth_host(self):
        return CFG_DEF_LEGACY_AUTH_HOST

    def set_legacy_auth_host(self, auth_host):
        self.conf.set(CFG_SEC_DEF, "auth_host", auth_host)

    def get_default_tenant(self):
        return self.conf.get(CFG_SEC_DEF, "tenant")

    def set_default_tenant(self, tenant):
        self.conf.set(CFG_SEC_DEF, "tenant", tenant)

    def get_default_api_ver(self):
        return self.conf.get(CFG_SEC_DEF, "api_ver")

    def set_default_api_ver(self, api_ver):
        self.conf.set(CFG_SEC_DEF, "api_ver", api_ver)

    def check_version(self):
        res_ver = requests.get(self.api_url() + INFO)
        json_ver = json.loads(res_ver.text)
        expected_ver = json_ver['ncloud_version'].lower() \
            .lstrip(string.ascii_lowercase)
        this_ver = SHORT_VERSION.lower().lstrip(string.ascii_lowercase)
        try:
            if LooseVersion(this_ver) < LooseVersion(expected_ver):
                print('Your ncloud version is outdated. '
                      'Please upgrade with "ncloud upgrade".')
        except AttributeError:  # master probably
            pass

    def silent_migration(self):
        # silentmigration TEMPORARY
        conf = self.conf
        auth_host = self.get_legacy_auth_host()
        if not conf.has_option(auth_host, "client_id"):
            try:
                conf.set(auth_host, "client_id", CFG_DEF_AUTH0_ID)
            except:
                return False
            if (not conf.has_option(auth_host, "username") and
                    conf.has_option(auth_host, "email")):
                conf.set(auth_host, "username",
                         conf.get(auth_host, "email"))
            self.set_default_auth_host(CFG_DEF_AUTH_HOST)

            print("Your account has been migrated to our new authentication "
                  "scheme. To access your account, please reset your "
                  "password using 'ncloud user pwreset <youremail>', or "
                  "contact support@nervanasys.com.")
            self._write_config(conf)

    def get_credentials(self):
        data = {}
        conf = self.conf
        section = self.get_selected_section()
        tenant = self.get_tenant()

        # password is now an optional item
        if conf.has_option(section, "password"):
            data["password"] = conf.get(section, "password")

        for item in ["username", "tenant", "client_id"]:
            if (item == "tenant" and tenant is not None and
                (not conf.has_option(section, item) or
                 conf.get(section, item) != tenant)):
                conf.set(section, item, tenant)
            if not conf.has_option(section, item):
                logger.warning("Can't generate auth token.  "
                               "Missing {} in {}".format(item, section))
                logger.warning("Re-run: {0} configure".format(CMD_NAME))
                sys.exit(1)
            data[item] = conf.get(section, item)
        return data

    def token_req(self, data=None):
        self.silent_migration()
        auth_host = self.get_default_auth_host()

        if data is None:
            data = self.get_credentials()

        if "password" not in data:
            # passwordless path
            ndata = {}
            ndata["connection"] = "email"
            ndata["send"] = "code"
            ndata["email"] = data["username"]
            ndata["client_id"] = data["client_id"]
            res = requests.post(auth_host + "/passwordless/start", data=ndata)
            data["password"] = '{}'.format(
                raw_input("Please enter code from email: "))
            data["connection"] = "email"
        else:
            data["connection"] = "Username-Password-Authentication"

        # Populate openid data constants
        data["scope"] = "openid"
        data["grant_type"] = "password"

        try:
            self.check_version()
            # Get the ncloud id_token
            res = requests.post(auth_host + AUTHENTICATION, data=data)

            if res.status_code == 200:
                res = json.loads(res.text)
                return res["id_token"]
            elif not str(res.status_code).startswith('2'):
                print_error(res)
        except requests.exceptions.RequestException as re:
            logger.error(re)
            sys.exit(1)

    def get_token(self, refresh=False, data=None):
        token = None
        conf = self.conf
        section = self.get_selected_section()
        tenant = self.get_tenant()
        if (conf.has_option(section, "token") and
                conf.has_option(section, "tenant") and
                conf.get(section, "tenant") == tenant):
            token = conf.get(section, "token")

        if refresh or not token:
            token = self.token_req(data)
            conf.set(section, "token", token)
            self._write_config(conf)

        return token

    def api_url(self):
        """
        Helper to return the base API url endpoint
        """
        return self.get_host() + PATH + self.get_default_api_ver()

    def token_url(self):
        """
        Helper to return the auth API url endpoint
        """
        return self.api_url() + TOKENS

    # silentmigration
    def legacy_token_url(self):
        """
        Helper to return the auth API url endpoint
        """
        return self.api_url() + LEGACY_TOKENS

    def _validate_config(self, conf):
        """
        Helper that ensures config items are in a compliant format.
        Usually comes about when upgrading and an older .ncloudrc
        is present

        Args:
            conf (SafeConfigParser): loaded config values.

        Returns:
            SafeConfigParser: valid, loaded config values.
        """
        # v0 -> v1 changes:
        api_ver = conf.get(CFG_SEC_DEF, "api_ver")
        if api_ver == "v0":
            conf.set(CFG_SEC_DEF, "api_ver", "v1")
        for host_cfg in ["host", "auth_host"]:
            url = conf.get(CFG_SEC_DEF, host_cfg)
            if not url.startswith("http"):
                conf.set(CFG_SEC_DEF, host_cfg, "https://" + url)
        return conf

    def _load_config(self):
        """
        Helper to read and return the contents of the configuration file.
        Certain defaults may be defined and loaded here as well.

        Returns:
            SafeConfigParser: possibly empty configuration object
        """
        conf = configparser.SafeConfigParser({
            "host": CFG_DEF_HOST,
            "auth_host": CFG_DEF_AUTH_HOST,
            "api_ver": CFG_DEF_API_VER,
            "tenant": CFG_DEF_TENANT,
            "legacy_auth_host": CFG_DEF_LEGACY_AUTH_HOST
        })

        if os.path.isfile(CFG_FILE):
            if sys.platform != 'win32':
                if oct(os.stat(CFG_FILE)[stat.ST_MODE])[-2:] != "00":
                    # group, or other can rw or x config file.  Nag user
                    logger.warn("Insecure config file permissions found.  "
                                "Please run: chmod 0600 {}".format(CFG_FILE))
            conf.read([CFG_FILE])

        conf = self._validate_config(conf)
        return conf

    def _write_config(self, conf):
        """
        Writes the config settings to disk.

        Args:
            conf (SafeConfigParser): configuration settings.
        """
        with open(CFG_FILE, "w") as cf:
            conf.write(cf)
        if sys.platform != 'win32':
            os.chmod(CFG_FILE, 0o600)
