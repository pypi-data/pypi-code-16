import yaml


class Config(object):
    def __init__(self):
        with open('/etc/py-build-server/config.yaml', 'r') as config_file:
            config = yaml.load(config_file)
        if isinstance(config, dict):
            self.repos = {name: Repo(name, conf) for name, conf in config.iteritems()}
        self._sanity_check()

    def get(self, name):
        return self.repos.get(name)

    def _sanity_check(self):
        if len(self.repos) < 1:
            raise Exception(msg='no repos detected in yaml')
        for name, repo in self.repos.iteritems():
            if repo.dir is None:
                raise Exception(msg='repo {} has no dir set'.format(name))


class Repo(object):
    def __init__(self, name, conf):
        self.name = name
        self.dir = conf.get('dir')
        self.fetch_frequency = conf.get('fetch_frequency', 10)
        self.branch = conf.get('branch')
        self.remote = conf.get('remote', 'origin')
        self.twine_conf = conf.get('twine_conf')
        self.build_command = conf.get('build_cmd', 'python setup.py sdist')
