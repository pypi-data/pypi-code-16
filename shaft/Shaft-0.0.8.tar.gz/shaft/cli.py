"""
________________________________________________________________________________

  /$$$$$$  /$$   /$$  /$$$$$$  /$$$$$$$$ /$$$$$$$$
 /$$__  $$| $$  | $$ /$$__  $$| $$_____/|__  $$__/
| $$  \__/| $$  | $$| $$  \ $$| $$         | $$
|  $$$$$$ | $$$$$$$$| $$$$$$$$| $$$$$      | $$
 \____  $$| $$__  $$| $$__  $$| $$__/      | $$
 /$$  \ $$| $$  | $$| $$  | $$| $$         | $$
|  $$$$$$/| $$  | $$| $$  | $$| $$         | $$
 \______/ |__/  |__/|__/  |__/|__/         |__/

https://github.com/mardix/shaft

________________________________________________________________________________
"""

import os
import re
import sys
import traceback
import logging
import importlib
import pkg_resources
import click
import yaml
import functools
import sh
import json
from werkzeug import import_string
from .__about__ import *
from shaft import utils
import flask
from .core import db

CWD = os.getcwd()
SKELETON_DIR = "skel"
APPLICATION_DIR = "%s/app" % CWD
APPLICATION_DATA_DIR = "%s/var" % APPLICATION_DIR
APPLICATION_BABEL_DIR = "%s/babel" % APPLICATION_DATA_DIR

class CLI(object):
    """
    For command line classes in which __init__ contains all the functions to use

    example

    class MyCLI(ShaftCLI):
        def __init__(self):

            @cli.command()
            def hello():
                click.echo("Hello world")

            @cli.command()
            @click.argument("name")
            def say_my_name(name):
                click.echo("My name is %s" % name)
    """
    pass


def get_project_dir_path(project_name):
    return "%s/%s" % (APPLICATION_DIR, project_name)


def copy_resource_dir(src, dest):
    """
    To copy package data directory to destination
    """
    package_name = "shaft"
    dest = (dest + "/" + os.path.basename(src)).rstrip("/")
    if pkg_resources.resource_isdir(package_name, src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        for res in pkg_resources.resource_listdir(__name__, src):
            copy_resource_dir(src + "/" + res, dest)
    else:
        if not os.path.isfile(dest) and os.path.splitext(src)[1] not in [".pyc"]:
            copy_resource_file(src, dest)


def copy_resource_file(src, dest):
    with open(dest, "wb") as f:
        f.write(pkg_resources.resource_string(__name__, src))

# ------------------------------------------------------------------------------
application = None


def get_propel_config(cwd, key):
    with open("%s/%s" % (cwd, "propel.yml")) as f:
        config = yaml.load(f)
    return config.get(key)


def get_push_remotes_list(cwd, key=None):
    """
    Returns the remote hosts in propel
    :param cwd:
    :param key:
    :param file:
    :return: list
    """
    config = get_propel_config(cwd, "deploy-remotes")
    return config[key] if key else [v for k, l in config.items() for v in l]


def git_push_to_master(cwd, hosts, name="all", force=False):
    """
    To push to master
    :param cwd:
    :param hosts:
    :param force:
    :return:
    """

    def process_output(line):
        print(line)

    with sh.pushd(cwd):
        name = "shaft_deploy_%s" % name

        if sh.git("status", "--porcelain").strip():
            raise Exception("Repository is UNCLEAN. Commit your changes")

        remote_list = sh.git("remote").strip().split()
        if name in remote_list:
            sh.git("remote", "remove", name)
        sh.git("remote", "add", name, hosts[0])

        if len(hosts) > 1:
            for h in hosts:
                sh.git("remote", "set-url", name, "--push", "--add", h)

        _o = ["push", name, "master"]
        if force:
            _o.append("--force")
        sh.git(*_o, _out=process_output)
        sh.git("remote", "remove", name)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def catch_exception(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as ex:
            print("-" * 80)
            print("Exception Uncaught")
            print("-" * 80)
            print(ex)
            print("-" * 80)
    return decorated_view


def cwd_to_sys_path():
    sys.path.append(CWD)


def project_name(name):
    return re.compile('[^a-zA-Z0-9_]').sub("", name)


def header(title=None):
    print(__doc__)
    print("v. %s" % __version__)
    print("_" * 80)
    if title:
        print("** %s **" % title)


def build_assets(app):
    from webassets.script import CommandLineEnvironment
    assets_env = app.jinja_env.assets_environment
    log = logging.getLogger('webassets')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)
    cmdenv = CommandLineEnvironment(assets_env, log)
    cmdenv.build()


@click.group()
def cli():
    """ Shaft (http://mardix.github.io/shaft) """

@click.group()
def cli_user():
    """ Shaft (http://mardix.github.io/shaft) """


@cli.command("init")
@catch_exception
def init():
    """  Setup Shaft in the current directory """

    shaftpyfile = os.path.join(os.path.join(CWD, "shaft_init.py"))

    header("Initializing Shaft ...")
    if os.path.isfile(shaftpyfile):
        print("WARNING: It seems like Shaft is already setup!")
        print("*" * 80)
    else:
        print("")
        print("Copying files to the current directory...")
        copy_resource_dir(SKELETON_DIR + "/create/", CWD)
        print("")

        _npm_install_static()
        print("")
        print("----- That was so Shaft! ----")
        print("")
        print("- Shaft is now setup")
        print("")
        print("> What's next?")
        print("- Edit the config [ app/config.py ] ")
        print("- If necessary edit and run the command [ shaft db-sync ]")
        print("- Launch app on development mode, run [ shaft serve ]")
        print("")
        print("*" * 80)

@cli.command("addview")
@click.argument("name")
@click.option("--no-template", "-t", is_flag=True, default=False)
def add_view(name, no_template):
    """ Create a new view and template page """

    app_dest = os.path.join(CWD, "app")
    viewsrc = "%s/create-view/view.py" % SKELETON_DIR
    tplsrc = "%s/create-view/template.jade" % SKELETON_DIR
    viewdest_dir = os.path.join(app_dest, "views")
    viewdest = os.path.join(viewdest_dir, "%s.py" % name)
    tpldest_dir = os.path.join(app_dest, "templates/%s/Index" % name)
    tpldest = os.path.join(tpldest_dir, "index.jade")

    header("Adding New View")
    print("View: %s" % viewdest.replace(CWD, ""))
    if not no_template:
        print("Template: %s" % tpldest.replace(CWD, ""))
    else:
        print("* Template will not be created because of the flag --no-template| -t")
    if os.path.isfile(viewdest) or os.path.isfile(tpldest):
        print("*** ERROR: View or Template file exist already")
    else:
        if not os.path.isdir(viewdest_dir):
            utils.make_dirs(viewdest_dir)
        copy_resource_file(viewsrc, viewdest)

        if not no_template:
            if not os.path.isdir(tpldest_dir):
                utils.make_dirs(tpldest_dir)
            copy_resource_file(tplsrc, tpldest)

    print("")
    print("*" * 80)

@cli.command("serve")
@click.option("--port", "-p", default=5000)
@catch_exception
def server(port):
    """ Serve application in development mode """

    header("Serving application in development mode ... ")
    print("")
    print("- Port: %s" % port)
    print("")
    cwd_to_sys_path()
    application.app.run(debug=True, host='0.0.0.0', port=port)

@cli.command("db-sync")
def db_sync():
    """ Sync database Create new tables etc... """

    print("Syncing up database...")
    cwd_to_sys_path()
    if application.app.db and application.app.db.Model:
        application.app.db.create_all()
        for m in application.app.db.Model.__subclasses__():
            if hasattr(m, "_syncdb"):
                print("Sync up model: %s ..." % m.__name__)
                getattr(m, "_syncdb")()

    print("Done")

def _set_flask_alembic():
    from flask_alembic import Alembic

    """ Add the SQLAlchemy object in the global extension """
    application.app.extensions["sqlalchemy"] = type('', (), {"db": db})
    alembic = Alembic()
    alembic.init_app(application.app)
    return alembic



#@cli.command("db-migrate")
def db_migrate():
    """Migrate DB """
    print("Not ready for use")
    exit()
    cwd_to_sys_path()
    alembic = _set_flask_alembic()
    with application.app.app_context():
        p = application.app.db.Model.__subclasses__()
        print(p)

        # Auto-generate a migration
        alembic.revision('making changes')

        # Upgrade the database
        alembic.upgrade()


@cli.command("assets2s3")
@catch_exception
def assets2s3():
    """ Upload assets files to S3 """
    import flask_s3

    header("Assets2S3...")
    print("")
    print("Building assets files..." )
    print("")
    build_assets(application.app)
    print("")
    print("Uploading assets files to S3 ...")
    flask_s3.create_all(application.app)
    print("")


@cli.command("deploy")
@click.option("--site", "-s", default=None)
@click.option("--remote", "-r", default=None)
@click.option("--force", "-f", is_flag=True, default=False)
@catch_exception
def deploy(site, remote, force):
    """ To deploy application to a git repository """

    if site:
        pass
    else:
        remote_name = remote or "ALL"
        print("Deploying application to remote: %s " % remote_name)
        print("...")
        hosts = get_push_remotes_list(CWD, remote or None)
        git_push_to_master(cwd=CWD, hosts=hosts, name=remote_name, force=force)
        print("Done!")


@cli.command("version")
def version():
    print("-" * 80)
    print(__version__)
    print("-" * 80)

# @cli.command("babel-build")
# def babelbuild():
#     print("Babel Build....")
#     #sh.pybabel()

def _npm_install_static():
    print("NPM Install packages...")
    static_path = os.path.join(CWD, "app/static")
    package_json = os.path.join(static_path, "package.json")

    try:
        if os.path.isfile(package_json):
            with sh.pushd(static_path):
                sh.npm("install", "-f")
        else:
            print("**ERROR: Can't install static files, `package.json` is missing at `%s`" % package_json)
            print("*" * 80)
    except sh.CommandNotFound as e:
        print("")
        print("*** Error Command Not Found: `{0}` is not found. You need to install `{0}` to continue".format(str(e)))
        print("*" * 80)

@cli.command("npm-install")
def install_static():
    """ Install NPM Packages for the front end in the /static/ dir"""
    _npm_install_static()


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def cmd():
    """
    Help to run the command line
    :return:
    """
    global application

    shaftpyfile = os.path.join(os.path.join(CWD, "shaft_init.py"))
    if os.path.isfile(shaftpyfile):
        cwd_to_sys_path()
        application = import_string("shaft_init")
    else:
        print("-" * 80)
        print("** Missing << 'shaft_init.py' >> @ %s" % CWD)
        print("-" * 80)

    if "shaftcli" in sys.argv[0]:
        [cmd(cli_user.command, click) for cmd in CLI.__subclasses__()]
        cli_user()
    else:
        cli()

