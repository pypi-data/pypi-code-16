import subprocess

import sys


class NosetestRunner(object):
    command = 'nosetests -v'

    def __init__(self, repo, config):
        self.repo = repo
        self.framework = config.framework
        self.dir = config.dir

    def run(self):
        result = subprocess.check_output(
            'cd {}; {}'.format(self.dir, self.command), shell=True).decode(encoding=sys.getdefaultencoding())
        self.repo.logger.debug(result)
        if 'FAILED' in result:
            return False
        # TODO: hook into test pass API
        return True
