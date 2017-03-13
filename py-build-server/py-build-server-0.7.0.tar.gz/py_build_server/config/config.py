import sys
import yaml
import logging


class Config(object):
    def __init__(self):
        with open('/etc/py-build-server/config.yaml', 'r') as config_file:
            config = yaml.load(config_file)

        if isinstance(config, dict):
            self.logging = Logging(config.get('logging', {}))
            self.repos = {name: Repo(name, conf) for name, conf in
                          config.get('repositories', {}).items()}
            self.update_method = UpdateMethod(config.get('repository_update_method', 'polling'))
            self.api = Api(config.get('api', {}))

        self._sanity_check()
        logging.basicConfig(level=self.logging.level)

    def get(self, name):
        return self.repos.get(name)

    def _sanity_check(self):
        if len(self.repos) < 1:
            raise Exception(msg='no repos detected in yaml')
        for name, repo in self.repos.items():
            if repo.dir is None:
                raise Exception(msg='repo {} has no dir set'.format(name))


class UpdateMethod(object):
    class Method(object):
        def __init__(self, conf):
            self.subdomain = conf.get('subdomain')
            self.listen_address = conf.get('listen_address')
            self.port = conf.get('port')

    def __init__(self, conf):
        self.methods = {}
        for method in ('github_webhook', 'bitbucket_webhook'):
            if method in conf:
                c = conf.get(method)
                self.methods[method] = self.Method(c)
        if 'polling' in conf:
            self.methods['polling'] = 'polling'


class Logging(object):
    def __init__(self, conf):
        try:
            level_map = logging._nameToLevel
        except:
            level_map = logging._levelNames
        self.level = level_map.get(conf.get('level', 'info').upper())


class Repo(object):
    class Tests(object):
        def __init__(self, conf):
            self.framework = conf.get('framework')
            self.dir = conf.get('dir')

    def __init__(self, name, conf):
        self.name = name
        self.dir = conf.get('dir')
        self.fetch_frequency = conf.get('interval', 10)
        self.update_method = conf.get('update_method')
        self.branch = conf.get('branch')
        self.remote = conf.get('remote', 'origin')
        self.twine_conf = conf.get('twine_conf')
        self.tests = [self.Tests(t) for t in conf.get('tests', {})]


class Api(object):
    def __init__(self, conf):
        self.listen_address = conf.get('listen_address')
        self.subdomain = conf.get('subdomain')
        self.port = conf.get('port')
        self.strict_port_checking = conf.get('strict_port_checking', False)
