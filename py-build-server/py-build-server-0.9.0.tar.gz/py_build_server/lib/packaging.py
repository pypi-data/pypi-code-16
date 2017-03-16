import subprocess


class PackageBuilder(object):
    def __init__(self, repo, config=None):
        self.repo = repo
        self.build_command = config.build_command.format(repository_dir=self.repo.working_dir)
        self.upload_command = config.upload_command.format(repository_dir=self.repo.working_dir)
        self.cleanup_command = config.cleanup_command.format(repository_dir=self.repo.working_dir)

    def build_and_upload(self):
        success = True
        try:
            self.repo.logger.debug('executing build command: {}'
                                   .format(self.build_command))
            out = subprocess.check_output(self.build_command, shell=True)
            self.repo.logger.debug(out)
            self.repo.logger.debug('executing upload command: {}'
                                   .format(self.upload_command))
            out = subprocess.check_output(self.upload_command, shell=True)
            self.repo.logger.debug(out)
        except subprocess.CalledProcessError:
            success = False
            self.repo.logger.error('error uploading file to pypi')
        finally:
            self.repo.logger.debug('executing cleanup command: {}'
                                   .format(self.cleanup_command))
            out = subprocess.check_output(self.cleanup_command, shell=True)
            self.repo.logger.debug(out)
        return success
