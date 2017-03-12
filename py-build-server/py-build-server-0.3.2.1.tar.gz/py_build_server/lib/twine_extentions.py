import subprocess


class Twine(object):
    def __init__(self, repo):
        self.repo = repo

    def upload(self, call):
        success = True
        try:
            subprocess.check_output(
                'cd {}; python2 setup.py sdist'.format(call.repo_dir), shell=True)
            subprocess.check_output(str(call), shell=True)
        except subprocess.CalledProcessError:
            success = False
            self.repo.logger.error('error uploading file to pipy')
        finally:
            subprocess.check_output(
                'rm -rf {}/dist'.format(call.repo_dir), shell=True)
        return success


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
        return 'twine upload {} {}'.format(self.dist, ' '.join(call_params))

    def load_yaml_config(self, config):
        for key in config.keys():
            assert key in self.__dict__
        self.__dict__.update(config)
