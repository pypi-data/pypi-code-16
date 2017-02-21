# -*- coding: utf-8 -*-
from __future__ import absolute_import

from ..core.utils import try_subprocess_call
from ..config import config as app_conf

import docker

_client = docker.from_env()


def run(arguments, environ):
    command = ['docker', 'run'] + arguments
    command = ' '.join(command)
    return try_subprocess_call(command, environ=environ)


def stop(container_name):
    _client.stop(container_name)
    return True


def get_image(name, tag=app_conf.docker.default_local_tag):
    image_name = '{name}:{tag}'.format(name=name, tag=tag)
    image_list = _client.images()
    found_image = [i for i in image_list if i['RepoTags'] == [image_name]]

    image = next(iter(found_image), None)
    return image_name if image else None


def cleanse_image_tag(tag):
    tag = ''.join([c for c in tag if c not in app_conf.docker.invalid_tag_chars])
    tag = tag.replace('/', '.')
    return tag
