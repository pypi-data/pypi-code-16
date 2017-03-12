import yaml
import logging


class Config(object):
    def __init__(self):
        with open('/etc/py-build-server/config.yaml', 'r') as config_file:
            config = yaml.load(config_file)

        if isinstance(config, dict):
            self.logging = Logging(config.get('logging', {}))
            self.repos = {name: Repo(name, conf) for name, conf in
                          config.get('repositories', {}).iteritems()}
            self.update_method = config.get('repository_update_method', 'polling')

        self._sanity_check()
        logging.basicConfig(level=self.logging.level)

    def get(self, name):
        return self.repos.get(name)

    def _sanity_check(self):
        if len(self.repos) < 1:
            raise Exception(msg='no repos detected in yaml')
        for name, repo in self.repos.iteritems():
            if repo.dir is None:
                raise Exception(msg='repo {} has no dir set'.format(name))


class Logging(object):
    def __init__(self, conf):
        self.level = logging._levelNames.get(conf.get('level', 'info').upper())
        self.implement_journald = conf.get('implement_journald', False)


class Repo(object):
    def __init__(self, name, conf):
        self.name = name
        self.dir = conf.get('dir')
        self.fetch_frequency = conf.get('interval', 10)
        self.branch = conf.get('branch')
        self.remote = conf.get('remote', 'origin')
        self.twine_conf = conf.get('twine_conf')
