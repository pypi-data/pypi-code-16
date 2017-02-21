# -*- coding: utf-8 -*-
from .git import get_current_branch
from .git import get_current_commit

from ..domain.vendor import GitError
from . import docker

# @see: https://docs.travis-ci.com/user/environment-variables/
#
# Below are the list of TravisCI environment variables we use in our builds.
travis_branch = 'TRAVIS_BRANCH'
travis_commit = 'TRAVIS_COMMIT'
REQUIRED_TRAVIS_ENV = {
    travis_branch: get_current_branch,
    travis_commit: get_current_commit,
}


def cleanse_environ(environ):
    environ = environ.copy()
    if environ.get(travis_branch):
        environ[travis_branch] = docker.cleanse_image_tag(environ[travis_branch])
    return environ


def patch_environ(environ, required_travis_env=REQUIRED_TRAVIS_ENV):
    """Updates `environ` with TRAVIS vars to simulate a build environment."""
    environ = environ.copy()
    for env in required_travis_env:
        if environ.get(env) is not None:
            continue
        try:
            environ[env] = required_travis_env[env]()
        except GitError:
            environ[env] = None
    return environ
