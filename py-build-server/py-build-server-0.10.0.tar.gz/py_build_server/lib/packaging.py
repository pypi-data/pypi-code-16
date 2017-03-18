import subprocess

import sys


class PackageBuilder(object):
    def __init__(self, repo, config=None):
        self.build_in_progress = False
        self.repo = repo
        self.build_command = config.build_command.format(repository_dir=self.repo.working_dir)
        self.upload_command = config.upload_command.format(repository_dir=self.repo.working_dir)
        self.cleanup_command = config.cleanup_command.format(repository_dir=self.repo.working_dir)

    def build_and_upload(self):
        self.build_in_progress = True
        build_out = self._run(build_command=self.build_command)
        upload_out = self._run(upload_command=self.upload_command) if build_out else False
        cleanup_out = self._run(cleanup_command=self.cleanup_command)

        return (all([build_out, upload_out]),
                self._combine_if_str(build_out, upload_out, cleanup_out))

    @staticmethod
    def _combine_if_str(*args):
        return '\n'.join([arg for arg in args])

    def _run(self, **kwargs):
        for name, command in kwargs.items():
            try:
                self.repo.logger.debug('executing %s: %s' % (name, command))
                bytes_out = subprocess.check_output(command, shell=True)
                out = bytes_out.decode(sys.stdout.encoding)
                self.repo.logger.debug(out)
                return out
            except subprocess.CalledProcessError:
                self.repo.logger.error('error executing %s: %s' % (name, command))
                return ''
