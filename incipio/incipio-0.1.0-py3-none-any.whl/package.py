"""Tools for creating Python packages, of the kind you might find on PyPI."""

import os
import subprocess
from datetime import datetime

def create_package(package, location, git=True, env=False, author=None, test=True, license="mit"):
    """Creates a new Python package.

    :param str package: The name of the package.
    :param str location: The location in file space that the package should be\
    created in.
    :param bool git: If True, the package will be made a Git repository. You\
    need to have git installed for this to work.
    :param env: If True, a virtual environment will be created. If a string is\
    given, that will be the name of the environment.
    :param str author: The name of the package author.
    :param bool test: If True, a test directory will be created.
    :param str license: The kind of license to use. Options are 'mit',\
    'apache', or 'gnu'."""

    if not isinstance(package, str):
        raise TypeError("package name must be str, not '%s'" % str(package))
    if not isinstance(location, str):
        raise TypeError("location must be str, not '%s'" % str(location))
    os.makedirs("%s%s%s" % (location, os.path.sep, package))
    if git:
        git_init(os.path.sep.join([location, package]))
        git_ignore(os.path.sep.join([location, package]))
    if env is True:
        create_env(os.path.sep.join([location, package]))
    elif env:
        create_env(os.path.sep.join([location, package]), name=env)
    create_python_package(
     os.path.sep.join([location, package]), package, author=author
    )
    if test: create_test_directory(os.path.sep.join([location, package]))
    if license:
        create_license(
         os.path.sep.join([location, package]), license, author if author else ""
        )


def git_init(location):
    """Initialises a git repository in the specified location. Git must be
    installed for this to work.

    :param str location: The directory to turn into a repository."""

    if not isinstance(location, str):
        raise TypeError("location must be str, not '%s'" % str(location))
    with open(os.devnull, 'w') as FNULL:
        subprocess.call("git init %s" % location, shell=True, stdout=FNULL)


def git_ignore(location, ignore=None):
    """Adds a .gitignore file in the specified location, with some sensible
    defaults.

    :param str location: The directory to add the file to.
    :param list ignore: A list of items to add to the .gitignore file."""

    if ignore is not None and not isinstance(ignore, list):
        raise TypeError("ignore argument only accepts lists")
    ignore = ignore if ignore else []
    with open(os.path.sep.join([location, ".gitignore"]), "w") as f:
        f.write("\n".join([
         "*.pyc",
         "__pycache__",
         ".DS_Store",
         "*env",
         "build",
         "_static",
         "_templates",
         "dist",
         "*.egg-info",
        ] + ignore))


def create_env(location, name="env"):
    """Creates a virtual environment.

    :param str location: The directory to add the env to.
    :param str name: The name of the environment."""

    with open(os.devnull, 'w') as FNULL:
        subprocess.call(
         "virtualenv -p python3 %s" % os.path.sep.join([location, name]),
         shell=True,
         stdout=FNULL
        )


def create_python_package(location, name, author=None):
    """Creates the actual importable Python package, with an __init__.py.

    :param str location: The directory to add the package to.
    :param str name: The name of the package.
    :param str author: The name of the package author."""

    os.makedirs("%s%s%s" % (location, os.path.sep, name))
    with open(os.path.sep.join([location, name, "__init__.py"]), "w") as f:
        f.write('version = "0.1.0"\n')
        if author: f.write('author = "%s"' % author)


def create_test_directory(location):
    """Creates a test directory.

    :param str location: The directory to add the tests to."""

    os.makedirs("%s%s%s" % (location, os.path.sep, "tests"))
    with open(os.path.sep.join([location, "tests", "__init__.py"]), "w") as f:
        f.write("")


def create_license(location, license, author):
    """Creates a license file.

    :param str location: The directory to add the file to.
    :param str license: The kind of license to create. Valid options are 'mit',\
    'apache', or 'gnu'.
    :param str author: The author of the package."""
    
    here = os.path.dirname(os.path.realpath(__file__))
    contents = None
    if license == "mit":
        with open(here + "/MIT") as f:
            contents = f.read() % (datetime.now().year, author)
    elif license == "apache":
        with open(here + "/apache") as f:
            contents = f.read() % (datetime.now().year, author)
    elif license == "gnu":
        with open(here + "/GNU") as f:
            contents = f.read() % (datetime.now().year, author)
    else:
        raise ValueError(
         "'%s' isn't a license incipio knows about." % str(license)
        )
    with open(os.path.sep.join([location, "LICENSE"]), "w") as f:
        f.write(contents)
