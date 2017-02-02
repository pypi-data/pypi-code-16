#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

# noinspection PyUnresolvedReferences
from six.moves import configparser
import os

ROLE_INACTIVE = "inactive"  # Can do NOTHING
ROLE_ADMIN = "admin"  # Can do ANYTHING
ROLE_POWER_READONLY = "power_readonly"  # Special user that can access (readonly) all tenants
ROLE_OWNER = "owner"  # Owner of a tenant. Can register collector and administer users
ROLE_UPLOAD = "upload"  # Collector permission. Can only upload files on behalf of tenant
ROLE_USER = "user"  # Regular user, can access the regular, read-only APIs
ROLE_LAMBDA = "lambda"  # Special user, used by Lambda services to keep track of system status

role_search_order = {
    "admin": ["admin"],
    "power_readonly": ["power_readonly", "admin"],
    "owner": ["owner", "admin"],
    "user": ["user", "owner", "admin"],
    "lambda": ["lambda", "admin"],
    "upload": ["upload", "user", "owner", "admin"],
}


def read_local_credentials(role="admin", home_dir=None):
    assert role in role_search_order.viewkeys(), "Unsupported role '{}'".format(role)

    credentials_file_name = "credentials"

    home_dir = home_dir or os.path.expanduser("~")

    # Load the file (will load empty if file does not exist)
    credentials_path = os.path.join(home_dir, ".itculate", credentials_file_name)
    config = configparser.ConfigParser()
    config.read([credentials_path])

    # Search in all matching roles
    for r in role_search_order[role]:
        try:
            api_key = config.get(r, "api_key")
            api_secret = config.get(r, "api_secret")

            return api_key, api_secret

        except configparser.NoSectionError:
            pass

        except configparser.NoOptionError:
            pass

    return None, None
