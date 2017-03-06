import click
import os


class Settings(object):

    APP_DIR = 'AexeaCli'

    _filepath = None

    @classmethod
    def _get_filename(cls, key):
        if cls._filepath is None:
            cls._filepath = click.get_app_dir(cls.APP_DIR)
            if not os.path.exists(cls._filepath):
                os.makedirs(cls._filepath, exist_ok=True)
        return os.path.join(cls._filepath, '{}.setting'.format(key))

    @classmethod
    def get(cls, key, defaultvalue=None):
        filename = cls._get_filename(key)
        if os.path.isfile(filename):
            if os.access(filename, os.R_OK):
                with open(filename, 'r', encoding='UTF-8') as f:
                    content = f.read()
                    return content
        if not defaultvalue is None:
            return defaultvalue
        raise click.ClickException('Key {} not found'.format(key))

    @classmethod
    def set(cls, key, value):
        filename = cls._get_filename(key)
        if (not os.path.exists(filename)) or os.access(filename, os.W_OK):
            with open(filename, 'w', encoding='UTF-8') as f:
                f.write(value)
            return
        raise click.ClickException('could not set value')

    @classmethod
    def remove(cls, key):
        filename = cls._get_filename(key)
        if os.path.exists(filename):
            os.unlink(filename)
