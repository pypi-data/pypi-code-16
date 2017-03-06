import click

from .settings import Settings


class CliData(object):
    def __init__(self):
        self._auth_token = None
        self._training = None

    @property
    def training(self):
        if self._training is None:
            if not self.auth_token:
                raise click.ClickException('no auth token specified')
        return self._training

    @training.setter
    def training(self, value):
        self._training = value

    @property
    def auth_token(self):
        if not self._auth_token is None:
            return self._auth_token
        token = Settings.get('auth_token', '')
        if token:
            self._auth_token = token
            return token
        raise click.ClickException(
            'auth token was not set\n\n'
            'set it globally with\n'
            '$ axel set auth_token YOURTOKEN\n\n'
            'or set it just for this request using\n'
            '$ axel COMMAND auth_token YOURTOKEN [...]')

    @auth_token.setter
    def auth_token(self, value):
        self._auth_token = value

    def save_auth_token(self):
        Settings.set('auth_token', self._auth_token)

pass_data = click.make_pass_decorator(CliData, ensure=True)
