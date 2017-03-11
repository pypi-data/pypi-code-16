from git import Repo


class ExtendedRepo(Repo):
    def __init__(self, config=None, name=None, *args, **kwargs):
        assert name is not None
        assert config is not None
        super(ExtendedRepo, self).__init__(path=config.dir, *args, **kwargs)
        self.name = name
        self.config = config
        assert not self.bare

    @staticmethod
    def build_repos_from_config(config):
        return [ExtendedRepo(name=name, config=repo_config) for name, repo_config in config.repos.iteritems()]

    def get_status(self):
        self.get_remote().fetch()
        return self.status()

    def get_remote(self):
        return self.remote(self.config.remote)

    def status(self):
        return Status(self.git.status())


class Status(object):
    def __init__(self, status_string):
        self.branch = None
        self.up_to_date = False
        self.ahead = False
        self.behind = False
        self.new_files = []
        self.modified_files = []
        self.parse_string(status_string)

    def parse_string(self, string):
        for line in string.splitlines():  # type: str
            if line.startswith('On branch '):
                self.branch = line.split('On branch ')[1]
            elif line.startswith('Your branch is up-to-date'):
                self.up_to_date = True
            elif line.startswith('Your branch is ahead'):
                self.ahead = True
            elif line.startswith('Your branch is behind'):
                self.behind = True
            elif line.strip().startswith('new file'):
                self.new_files.append(line.split('new file:')[1].strip())
            elif line.strip().startswith('modified'):
                self.modified_files.append(line.split('modified:')[1].strip())
