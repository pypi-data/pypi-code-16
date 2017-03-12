import time
from git import Repo
from multiprocessing import Queue

from py_build_server.lib.file_operations import LatestTagFileParser
from py_build_server.lib.twine_extentions import UploadCall, Twine

from py_build_server.lib.logger import Logger


class ExtendedRepo(Repo):
    def __init__(self, config=None, name=None, *args, **kwargs):
        assert name is not None
        assert config is not None
        self.latest_tag = None
        super(ExtendedRepo, self).__init__(path=config.dir, *args, **kwargs)
        self.name = name
        self.config = config
        self.logger = Logger(self.name)
        self.queue = Queue()
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

    def upload(self, latest_tag):
        self.latest_tag = latest_tag
        try:
            if LatestTagFileParser.is_tag_in_file(self, self.latest_tag):
                return
            self.logger.info('pulling latest changes for {repo} from {remote}/{branch}'
                             .format(repo=self.name,
                                     remote=self.get_remote().name,
                                     branch=self.active_branch.name))

            self.get_remote().pull()
            if Twine(self).upload(UploadCall(self.working_dir, self.config.twine_conf)):
                LatestTagFileParser.set_tag_in_file(self, self.latest_tag)
            self.logger.debug('waiting {} minutes before checking again'.format(self.config.fetch_frequency))
            time.sleep(self.config.fetch_frequency * 60)
        except KeyboardInterrupt:
            self.logger.debug('exiting process for {}'.format(self.name))


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
