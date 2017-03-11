import os

from py_build_server.lib.file_operations import LatestTagFileParser


class Twine(object):
    def __init__(self, repo):
        self.latest_tag = None
        self.repo = repo

    def upload(self, call, tag):
        if LatestTagFileParser.is_tag_in_file(self.repo, tag):
            return
        os.popen('cd {}; python2 setup.py sdist'.format(call.repo_dir)).read()
        result = UploadCallResult(os.popen(str(call)))
        os.popen('rm -rf {}/dist'.format(call.repo_dir)).read()
        print(result)
        if result.exit_code == 0:
            self.latest_tag = tag
            LatestTagFileParser.set_tag_in_file(self.repo, tag)


class UploadCallResult(object):
    def __init__(self, result):
        for line in result.read().splitlines():
            if line.startswith('HTTPError'):
                self.exit_code = 1
        self.exit_code = 0


class UploadCall(object):
    def __init__(self, repo_dir, config=None):
        self.dist = '{}/dist/*'.format(repo_dir)  # type: str
        self.repo_dir = repo_dir
        self.username = None  # type: str
        self.password = None  # type: str
        self.repository = None  # type: str
        self.gpg_sign = None  # type: bool
        self.gpg_program = None  # type: str
        self.gpg_identity = None  # type: str
        self.comment = None  # type: str
        self.pypirc_file = None  # type: str
        self.skip_existing = None  # type: bool
        if config:
            self.load_yaml_config(config)

    def __str__(self):
        call_params = []
        if self.username:
            call_params.append('-u {}'.format(self.username))
        if self.password:
            call_params.append('-p {}'.format(self.password))
        if self.repository:
            call_params.append('-r {}'.format(self.repository))
        if self.gpg_sign:
            call_params.append('-s')
        if self.gpg_program:
            call_params.append('--sign-with {}'.format(self.gpg_program))
        if self.gpg_identity:
            call_params.append('-i {}'.format(self.gpg_identity))
        if self.comment:
            call_params.append('-c {}'.format(self.comment))
        if self.pypirc_file:
            call_params.append('--config-file {}'.format(self.pypirc_file))
        if self.skip_existing:
            call_params.append('--skip-existing')
        ret = 'twine upload {} {}'.format(self.dist, ' '.join(call_params))
        print(ret)
        return ret

    def load_yaml_config(self, config):
        for key in config.keys():
            assert key in self.__dict__
        self.__dict__.update(config)
