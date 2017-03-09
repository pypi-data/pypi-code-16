from json import dump, load
from os import path

from devip.utils import get_input, current_ip, cidr, console, require, log

SETTINGS_FILENAME = '~/.devip.json'
USER_DEFAULTS = {'temp': [], 'perm': []}


class Service(object):
    name = None
    default_settings = {}
    required_settings = []

    @staticmethod
    def _load_settings():
        if path.isfile(SETTINGS_FILENAME):
            with open(SETTINGS_FILENAME) as fp:
                settings = load(fp)
        else:
            settings = {}

        settings.setdefault('user', USER_DEFAULTS)
        return settings

    def __init__(self):
        settings = Service._load_settings()
        self.user = settings['user']

        setattr(self, 'name', self.name)

        attrs = self.default_settings.copy()

        if self.name in settings:
            attrs.update({k: v for k, v in settings[self.name].items() if v})

        for key, value in attrs.items():
            setattr(self, key, value)

    @log('Set up {name}...')
    def setup(self):
        data = Service._load_settings()
        data[self.name] = {}

        for key, default in self.default_settings.items():
            data[self.name][key] = get_input('Enter {name} {key}'.format(name=self.name, key=key), default)

        with open(SETTINGS_FILENAME, 'w') as fp:
            dump(data, fp, indent=2)

    @log('Show {list_name} IP addresses...', list_name='all')
    def show(self, list_name=None):
        data = {}

        if not list_name or list_name == 'temp':
            data['Temporary IPs'], _ = self._get_user_setting('temp')
        if not list_name or list_name == 'perm':
            data['Permanent IPs'], _ = self._get_user_setting('perm')

        for key, values in data.items():
            if not list_name:
                console('{}:'.format(key))
            if values:
                for value in values:
                    console('   * {}'.format(value))
            else:
                console('   No records')

    @log('Clear {list_name} IP addresses...', list_name='all')
    def clear(self, list_name=None):
        if not list_name or list_name == 'temp':
            self._update_user_setting_list('temp', None)
        if not list_name or list_name == 'perm':
            self._update_user_setting_list('perm', None)

    @log('Move to {list_name} IP address `{address}`', address=cidr(current_ip()), list_name='temp')
    def move(self, address, list_name=None):
        require(msg='Service `{}` requires settings to be set-up before use.'.format(self.name), **self.__dict__)
        list_name = list_name or 'temp'

        if not address:
            self._move_here(list_name)
        else:
            self._move_ip(list_name, address)

    def _move_here(self, list_name):
        self._move_ip(list_name, cidr(current_ip()))

    def _move_ip(self, list_name, ip):
        service_ips = self.get_service_ips()
        temp_ips = [cidr(x) for x in self.user['temp']]
        perm_ips = [cidr(x) for x in self.user['perm']]

        for x in temp_ips:
            if x in service_ips and x != ip:
                self.revoke_ip(x)

        for x in perm_ips + [ip]:
            if x not in service_ips:
                self.allow_ip(x)

        self.add(list_name, ip)
        self.remove(Service._other_list(list_name), ip)

    @staticmethod
    def _other_list(list_name):
        return 'perm' if list_name == 'temp' else 'temp'

    @log('Add IP address `{ip}` to {list_name}', ip='undefined', list_name='undefined')
    def add(self, list_name, ip):
        require(list=list_name, ip=ip)
        switcher = {
            'temp': lambda: self._update_user_setting_list('temp', ip),
            'perm': lambda: self._update_user_setting_list('perm', ip)
        }
        switcher[list_name]()

    @log('Remove IP address `{ip}` from {list_name}', ip='undefined', list_name='undefined')
    def remove(self, list_name, ip):
        require(list=list_name, ip=ip)
        switcher = {
            'temp': lambda: self._update_user_setting_list('temp', ip, remove=True),
            'perm': lambda: self._update_user_setting_list('perm', ip, remove=True)
        }
        switcher[list_name]()

    def _get_user_setting(self, key):
        settings = Service._load_settings()
        return settings['user'][key], settings

    def _update_user_setting(self, key, value, settings):
        settings['user'][key] = value

        with open(SETTINGS_FILENAME, 'w') as fp:
            dump(settings, fp, indent=2)

    def _update_user_setting_list(self, key, value, remove=False):
        source, settings = self._get_user_setting(key)
        if not value:
            source = []
        elif not remove:
            source.append(value)
        elif value in source:
            source.remove(value)
        target = list(set(source))
        self._update_user_setting(key, target, settings)

    def get_service_ips(self):
        raise NotImplementedError()

    def revoke_ip(self, ip):
        raise NotImplementedError()

    def allow_ip(self, ip):
        raise NotImplementedError()
