# -*- coding: utf-8 -*-
import os


class BlingConfig(object):
    @property
    def config_path(self):
        return os.path.abspath('./bling.json')

    @property
    def required_keys(self):
        return [
            'run',
            'start',
            'name',
            'packer',
        ]

    @property
    def optional_keys(self):
        return {
            'env': {},
            'packer_exec_path': 'packer',
        }


class CommandConfig(object):
    @property
    def run_command(self):
        """Command to execute when `docker run` is invoked."""
        return '/bin/bash'


class LockConfig(object):
    @property
    def lock_file_path(self):
        """Local path to store the md5 hash after checking for Packer changes."""
        return os.path.abspath('./.bling.lock')

    @property
    def tar_file_path(self):
        """Temporary tar file store location used to ref before the md5sum."""
        return os.path.abspath('./.lock.tar')


class PackerConfig(object):
    @property
    def tmp_root(self):
        return os.path.abspath('./.bling')

    @property
    def tmp_path(self):
        return os.path.join(self.tmp_root, 'template.updated.json')

    @property
    def config_file(self):
        return 'template.json'


class DockerConfig(object):
    @property
    def default_local_tag(self):
        return 'local'

    @property
    def invalid_tag_chars(self):
        return '!"#$%&\'()*+,:;<=>?@[\\]^`{|}~'


class Config(object):
    def __init__(self):
        self.bling = BlingConfig()
        self.commands = CommandConfig()
        self.lock = LockConfig()
        self.packer = PackerConfig()
        self.docker = DockerConfig()


config = Config()
