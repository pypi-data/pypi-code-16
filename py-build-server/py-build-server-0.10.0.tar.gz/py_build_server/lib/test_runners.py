import re
import subprocess

import sys


class TestRunner(object):
    def __init__(self, repo, config):
        self.repo = repo
        self.command = config.command.format(repository_dir=self.repo.working_dir)
        self.failure_regex = config.failure_regex
        self.success_regex = config.success_regex
        self.name = config.name

    def run(self):
        self.repo.logger.debug('executing test command: {}'
                               .format(self.command))
        result = subprocess.check_output(self.command, shell=True).decode(encoding=sys.getdefaultencoding())
        self.repo.logger.debug(result)
        if self.failure_regex:
            if re.match(self.failure_regex, result):
                return False, result
        # TODO: hook into test pass API
        if self.success_regex:
            if re.match(self.success_regex, result):
                return True, result
        self.repo.logger.info('unsure how to tell if test passed or failed, assuming it failed. Please check '
                              'your success_regex and failure_regex strings under tests in this repository')
