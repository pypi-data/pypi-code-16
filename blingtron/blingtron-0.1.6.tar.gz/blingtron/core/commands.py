# -*- coding: utf-8 -*-
import os

import blingrc

from .utils import try_subprocess_call
from .io import err, warn
from .lock import write_lock

from ..vendor import travis
from ..vendor import packer
from ..vendor import docker

from ..config import config as app_conf


def start(config, run_command=app_conf.commands.run_command):
    packer_path = config.get('packer')
    if packer.is_packer_updated(packer_path):
        warn('packer config has changed, re-run bling build')
        return False

    image_name = docker.get_image(config.get('image_name'))
    if not image_name:
        err('docker image for "%s" does not exist, run bling build' % image_name)
        return False

    write_lock(packer_path)
    command = config.get('start') + ['--name', config.get('name'), image_name, run_command]
    environ = blingrc.patch_environ(os.environ, config.get('env'))
    return docker.run(command, environ)


def stop(config):
    return docker.stop(config.get('name'))


def run(config):
    environ = blingrc.patch_environ(os.environ, config.get('env'))
    return try_subprocess_call(config.get('run'), environ=environ)


def build(config, should_publish=False, is_debug=False):
    packer_path = config.get('packer_exec_path')
    if not os.path.exists(packer_path):
        packer_path = app_conf.bling.optional_keys['packer_exec_path']
    command = packer.bootstrap_config(config, should_publish, is_debug, packer_exec_path=packer_path)

    environ = travis.patch_environ(os.environ)
    environ = travis.cleanse_environ(environ)
    environ = blingrc.patch_environ(environ, config.get('env'))

    is_success = try_subprocess_call(command, environ=environ)

    packer.cleanup_config()
    write_lock(config.get('packer'))
    return is_success
