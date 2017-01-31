import functools
import logging
import os
from lintreview.review import IssueComment
from lintreview.tools import Tool, run_command
from lintreview.utils import in_path, npm_exists

log = logging.getLogger(__name__)


class Eslint(Tool):

    name = 'eslint'

    def check_dependencies(self):
        """
        See if ESLint is on the system path.
        """
        return in_path('eslint') or npm_exists('eslint')

    def match_file(self, filename):
        """
        Check if a file should be linted using ESLint.
        """
        base = os.path.basename(filename)
        name, ext = os.path.splitext(base)
        return ext == '.js'

    def process_files(self, files):
        """
        Run code checks with ESLint.
        """
        log.debug('Processing %s files with %s', files, self.name)
        cmd = self.name
        if npm_exists('eslint'):
            cmd = os.path.join(os.getcwd(), 'node_modules', '.bin', 'eslint')
        command = [cmd, '--format', 'checkstyle']

        # Add config file or default to recommended linters
        if self.options.get('config'):
            command += ['--config', self.apply_base(self.options['config'])]

        command += files
        output = run_command(
            command,
            ignore_error=True)

        if output.startswith('Cannot read config file'):
            msg = u'Your eslint config file is missing or invalid. ' \
                   u'Please ensure that `{}` exists and is valid.'
            msg = msg.format(self.options['config'])
            return self.problems.add(IssueComment(msg))

        filename_converter = functools.partial(
            self._relativize_filename,
            files)
        self._process_checkstyle(output, filename_converter)
