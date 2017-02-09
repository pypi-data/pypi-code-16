# coding=utf-8
"""This is default settings."""

DEBUG = True


# This should be a unique random string. Don't share this with anyone.
# The key is used for signing cokies and for CSRF protection.
# To generate a key, you can for example use openssl:
# $ openssl rand -base64 32
# If the ky is not set, the sever will not start.
SECRET_KEY = u'YtBu+oAeAmMGyiNZb7o/L7xTwtjSwKGRQyVa79aB6ps='

# Commant the following line to unable cross domain.
ENABLED_CROSS_DOMAIN = True

# bcrypt_sha26/bcrypt
PASSWD_METHOD = 'bcrypt_sha256'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:@127.0.0.1/db_name'


from ebs_web.site_setting import *  # noqa: E402
