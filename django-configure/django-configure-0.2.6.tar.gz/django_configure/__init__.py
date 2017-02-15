# coding=utf-8
from __future__ import unicode_literals
import sys

import os

from django.utils.crypto import get_random_string

import django_configure.type
import ConfigParser

main_config = None


class ConfigParserDefault(ConfigParser.ConfigParser):
    def get(self, section, option, *args, **kwargs):
        try:
            return ConfigParser.ConfigParser.get(self, section, option)
        except Exception:
            return None


class DjangoConfig(object):
    def __init__(self, description_dict={}, env_prefix='', path=None, virtual_env_root=True):
        self.content = description_dict
        self.env_prefix = env_prefix
        self.virtual_env_root = virtual_env_root
        self.config_path = path
        self.config = ConfigParserDefault()

        if self.config_var_name in os.environ:
            self.config.read(os.environ[self.config_var_name])
        # we are not in virtualenv, or we explicitly do not want config path relative to virtual env
        if self.config_path is not None and os.path.exists(self.config_path):
            if not self.virtual_env_root and hasattr(sys, 'real_prefix'):
                self.config.read(self.config_path)
            else:
                # we are in virtual env
                virtualenv_root = os.path.dirname(os.path.dirname(sys.executable))
                self.config.read(os.path.join(virtualenv_root, self.config_path))

        if self.content:
            for section_id, section in self.content.items():
                if not isinstance(section, dict):
                    raise ValueError('Section descriptor is not a dict')

                for entry_id, entry in section.items():
                    if not isinstance(entry, django_configure.type.ConfigField):
                        raise ValueError('%s.%s - Entry is not inherited from django_configure.type.ConfigField' %
                                         (section_id, entry_id))
                    entry.init(env_prefix, section_id, entry_id, self.config)

    @property
    def config_var_name(self):
        return (self.env_prefix.upper() + '_' if self.env_prefix else '') + 'CONFIG'

    def get(self, descriptor):
        descriptor = descriptor.split('.')
        assert len(descriptor) == 2
        return self.content[descriptor[0]][descriptor[1]].get()

    def append(self, description_dict):
        if not self.content:
            self.content = description_dict
        else:
            for section_id, section in description_dict.items():
                if not isinstance(section, dict):
                    raise ValueError('Section descriptor is not a dict')

                if section_id not in self.content:
                    self.content[section] = {}

                for entry_id, entry in section.items():
                    if not isinstance(entry, django_configure.type.ConfigField):
                        raise ValueError('%s.%s - Entry is not inherited from django_configure.type.ConfigField' %
                                         (section_id, entry_id))
                    entry.init(self.env_prefix, section, entry_id, self.config)
                    self.content[section_id][entry_id] = entry

    def generate(self, generate_file=True, dev=False):
        output = ''
        for section_id, section in self.content.items():
            output += '[%s]\n' % section_id
            for entry_id, entry in section.items():
                output += '# %s\n' % entry.help
                output += '%s=%s\n' % (entry.id, entry.dev_default if dev else entry.default)
        if self.config_path and generate_file:
            try:
                os.makedirs(os.path.dirname(self.config_path))
            except Exception:
                pass
            path = self.config_path
            if os.path.exists(path):
                path += '.template'

            with open(path, mode='w') as f:
                f.write(output)

        return output

    def generate_wsgi(self, path=None):
        wsgi_template = ''
        with open(os.path.join(os.path.dirname(__file__), 'resources', 'wsgi.py.template'), mode='r') as wsgi_template_file:
            wsgi_template = wsgi_template_file.read()

        new_wsgi_content = wsgi_template % {'CONFIG_VAR_NAME': self.config_var_name, 'CONFIG_PATH': self.config_path}

        if path is not None:
            with open(path, mode='w') as wsgi_file:
                wsgi_file.write(new_wsgi_content)

        return new_wsgi_content


def check_config(config):
    if config.config_var_name not in os.environ:
        print('[WARNING] %s env variable is not set, if you run any manage.py task apart from createconfig stop now, '
              'and set %s to your application config (generated via \'manage.py createconfig\'' %
              (config.config_var_name, config.config_var_name))


def define(description_dict, default_path=None, env_prefix=''):
    global main_config
    main_config = DjangoConfig(description_dict, env_prefix=env_prefix, path=default_path)
    check_config(main_config)
    return main_config


def default(app_name, base_path, env_prefix='', default_path=None):
    def generate_secret():
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return get_random_string(50, chars)

    global main_config
    main_config = DjangoConfig({
        'Common': {
            'secret': django_configure.type.String('Secret for the application', default=generate_secret()),
            'static_root': django_configure.type.Path('Static root path (static files will be copied here)',
                                                      default='/var/lib/' + app_name + '/static/',
                                                      dev_default=os.path.join(base_path, 'static.root')),
            'static_url': django_configure.type.Url('Url to static files', default='/static/'),
            'media_root': django_configure.type.Path('Media root path (media files will be stored here)',
                                                     default='/var/lib/' + app_name + '/media/',
                                                     dev_default=os.path.join(base_path, 'media.root')),
            'media_url': django_configure.type.Url('Url to media files', '/media/'),
            'debug': django_configure.type.Boolean(help='if true debug mode will be enabled for the application, do not switch this in production',
                                                   default=False, dev_default=True)
        },
        'Database': {
            'url': django_configure.type.Database('Url to access database (including credentials)',
                                                  default='sqlite:////var/lib/'+app_name+'/'+app_name+'.sqlite',
                                                  dev_default='sqlite:///'+base_path+'/'+app_name+'.sqlite')
        }
    }, env_prefix=env_prefix, path=default_path)

    check_config(main_config)

    return main_config
