# Copyright 2015, 2016 Ben Sturmfels
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from fabric.api import abort, cd, env, hide, local, run, settings
from fabric.contrib.files import exists


def flush_memcached():
    """Clear cache by restarting the memcached server.

    By design, any user on the system can issue commands to memcached, including
    to flush the whole cache. Alternately, we could install libmemcached-tools
    and run `memcflush --servers localhost`.

    """
    run("echo flush_all | nc -w1 localhost 11211")


def prepare_django():
    with cd(env.project_dir):
        # Clear all Python bytecode, just in case we've upgraded Python.
        run('find -type d -name __pycache__ | xargs rm -rf') # Python 3
        run("find -type f -name '*.pyc' -print0 | xargs -0 rm -f") # Python 2

        # Test configuration before we attempt to restart the application server.
        run('{env.virtualenv}/bin/python manage.py check --deploy --settings={env.settings}'.format(
            env=env))

        # Collect static files.
        run('{env.virtualenv}/bin/python manage.py collectstatic --settings={env.settings} -v0 --noinput --clear'.format(
            env=env))

        # Migrate.
        run('{env.virtualenv}/bin/python manage.py migrate --settings={env.settings}'.format(
            env=env))


def prepare_virtualenv():
    """Initialise a virtualenv and install required Python modules."""

    if not exists(env.virtualenv):
        run("virtualenv --python={env.python} --system-site-packages {env.virtualenv}".format(env=env))
    with cd(env.project_dir):
        run("{env.virtualenv}/bin/pip install -r {env.requirements}".format(
            env=env))


def reload_uwsgi():
    run("sudo ln -s --force {env.project_dir}/{env.uwsgi_conf} /etc/uwsgi-emperor/vassals/{env.site_name}.ini".format(
            env=env))
    with cd(env.project_dir):
        run('touch {env.project_dir}/{env.uwsgi_conf}'.format(env=env))


def transfer_files_git():
    local("git push origin")
    with cd(env.project_dir):
        run('git init --quiet')
        run('git config receive.denyCurrentBranch ignore')
    local("git push {env.user}@{env.host}:{env.project_dir} master".format(
            env=env),
          capture=False)
    with cd(env.project_dir):
        run("git reset --hard")


def update_nginx():
    run("sudo ln -s --force {env.project_dir}/{env.nginx_conf} /etc/nginx/sites-available/{env.site_name}".format(
            env=env))
    run("sudo ln -s --force /etc/nginx/sites-available/{env.site_name} /etc/nginx/sites-enabled/{env.site_name}".format(
            env=env))
    run("sudo /usr/sbin/nginx -t")
    run("sudo /etc/init.d/nginx force-reload")


def lint():
    """Run Pylint over everything."""
    local('pylint --rcfile=pylint.conf $(find -type f -name \'*.py\')')


def grep_for_pdb():
    """Check that code doesn't ever call the debugger.

    Doing so in production would lock up worker processes.

    """
    with settings(hide('warnings', 'stderr'), warn_only=True):
        out = local("find -not -name fabfile.py -name '*.py' -print0 | xargs -0 grep -n '\\bpdb\\b'", capture=True)
    if out != '':
        print(out)
        abort("There's a call to pdb in the code. See output from grep above.")


def fix_permissions(read=None, read_write=None):
    """Ensure permissions are set correctly to run site as unprivileged user."""

    if read is None:
        read = []

    if read_write is None:
        read_write = []

    # Uploading user owns the files. Web server/app user has access via group.
    # Others have no access.
    with cd(env.project_dir):
        run('sudo chown --recursive {env.user}:{env.app_user} .'.format(env=env))
        run('sudo chmod --recursive u=rwX,g=,o= .')

        # Assume we always need read access to project directory.
        run('sudo chmod g+rX .')

        for path in read:
            run('sudo chmod --recursive g+rX {path}'.format(path=path))
        for path in read_write:
            run('sudo chmod --recursive g+rwX {path}'.format(path=path))
