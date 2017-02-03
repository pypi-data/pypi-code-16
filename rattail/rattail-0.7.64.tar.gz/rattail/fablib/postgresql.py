# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Fabric Library for PostgreSQL
"""

from __future__ import unicode_literals, absolute_import

import re

from fabric.api import sudo, run, get, hide

from rattail.fablib import apt


def install():
    """
    Install the PostgreSQL database service
    """
    apt.install('postgresql')


def get_version():
    """
    Fetch the version of PostgreSQL running on the target system
    """
    result = sudo('psql --version')
    if result.succeeded:
        match = re.match(r'^psql \(PostgreSQL\) (\d+\.\d+)\.\d+', result)
        if match:
            return float(match.group(1))


def sql(sql, database=''):
    """
    Execute some SQL as the 'postgres' user.
    """
    return sudo('sudo -u postgres psql --tuples-only --no-align --command="{0}" {1}'.format(sql, database), shell=False)


def user_exists(name):
    """
    Determine if a given PostgreSQL user exists.
    """
    user = sql("SELECT rolname FROM pg_roles WHERE rolname = '{0}'".format(name))
    return bool(user)


def create_user(name, password=None, checkfirst=True, createdb=False):
    """
    Create a PostgreSQL user account.
    """
    if not checkfirst or not user_exists(name):
        createdb = '--{}createdb'.format('' if createdb else 'no-')
        sudo('sudo -u postgres createuser {createdb} --no-createrole --no-superuser {name}'.format(
            createdb=createdb, name=name))
        if password:
            with hide('running'):
                sql("ALTER USER \\\"{0}\\\" PASSWORD '{1}';".format(name, password))


def db_exists(name):
    """
    Determine if a given PostgreSQL database exists.
    """
    db = sql("SELECT datname FROM pg_database WHERE datname = '{0}'".format(name))
    return db == name


def create_db(name, owner=None, checkfirst=True):
    """
    Create a PostgreSQL database.
    """
    if not checkfirst or not db_exists(name):
        args = '--owner={0}'.format(owner) if owner else ''
        sudo('sudo -u postgres createdb {0} {1}'.format(args, name), shell=False)


def drop_db(name, checkfirst=True):
    """
    Drop a PostgreSQL database.
    """
    if not checkfirst or db_exists(name):
        sudo('sudo -u postgres dropdb {0}'.format(name), shell=False)


def download_db(name, destination=None):
    """
    Download a database from the "current" server.
    """
    if destination is None:
        destination = './{0}.sql.gz'.format(name)
    run('touch {0}.sql'.format(name))
    run('chmod 0666 {0}.sql'.format(name))
    sudo('sudo -u postgres pg_dump --file={0}.sql {0}'.format(name), shell=False)
    run('gzip --force {0}.sql'.format(name))
    get('{0}.sql.gz'.format(name), destination)
    run('rm {0}.sql.gz'.format(name))
