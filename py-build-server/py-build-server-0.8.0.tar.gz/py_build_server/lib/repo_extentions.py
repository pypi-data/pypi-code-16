from git import Repo
from multiprocessing import Queue

from py_build_server.lib.file_operations import LatestTagFileParser
from py_build_server.lib.test_runners import TestRunner
from py_build_server.lib.twine_extentions import PackageBuilder

from py_build_server.lib.logger import Logger


class ExtendedRepo(Repo):
    """
    self.logger should always point back to the internal logger wrapper class
            - py_build_server.lib.logger.Logger()
    self.queue is used for inter-process communication. messages should be sent as json
            payloads. Required fields (and the currently supported params) are :
                keys
                -----
                - event: this is used by logic in main.PyBuildServer.wait_for_event()
                          to dispatch the event to the correct module
                    values
                    -------
                    - new_tag: triggers a build and upload of the repository
                        extra params supported:
                        -----------------------
                            - latest: tells the repo what tag has been detected as the
                                       latest
                    - stop: stops this repo's process from waiting for any more events
                             and exit

    """
    def __init__(self, config=None, name=None, *args, **kwargs):
        assert name is not None
        assert config is not None
        self.latest_tag = None  # type: str
        self.test_runners = []
        super(ExtendedRepo, self).__init__(path=config.dir, *args, **kwargs)
        self.name = name  # type: str
        self.config = config  # type: config.Repo
        self.logger = Logger(self.name)  # type: .Logger
        self.queue = Queue()  # type: Queue
        self.package_builder = PackageBuilder(self, self.config.release_conf)
        for test in self.config.tests:
            self.test_runners.append(TestRunner(self, test))
        assert not self.bare

    @staticmethod
    def build_repos_from_config(config):
        """
        returns a list of ExtendedRepo objects built from the Config object passed in
        :type config: Config()
        :return:
        """
        return [ExtendedRepo(name=name, config=repo_config) for name, repo_config in config.repos.items()]

    def to_dict(self):
        return dict(config=self.config.__dict__, name=self.name, active_branch=str(self.active_branch),
                    latest_tag=str(self.latest_tag))

    def get_status(self):
        self.get_remote().fetch()
        return self.status()

    def get_remote(self):
        return self.remote(self.config.remote)

    def status(self):
        return Status(self.git.status())

    def upload(self, latest_tag):
        old_tag = self.latest_tag
        self.latest_tag = latest_tag
        try:
            if LatestTagFileParser.is_tag_in_file(self, self.latest_tag):
                self.logger.debug('already at latest tag: {}'
                                  .format(self.latest_tag))
                return
            self.logger.info('pulling latest changes for {repo} from {remote}/{branch}'
                             .format(repo=self.name,
                                     remote=self.get_remote().name,
                                     branch=self.active_branch.name))

            self.get_remote().pull()
            for test in self.test_runners:
                if not test.run():
                    self.logger.info('tests did not pass, skipping upload')
                    self.latest_tag = old_tag
                    return
            if self.package_builder.build_and_upload():
                self.logger.info('uploaded {}:{} to pypi'.format(self.name, self.latest_tag))
                LatestTagFileParser.set_tag_in_file(self, self.latest_tag)
            else:
                self.logger.info('failed uploading {}:{} to pypi, rolling back latest tag'
                                 .format(self.name, self.latest_tag))
                self.latest_tag = old_tag

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
