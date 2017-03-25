#! python3
# encoding: utf-8

# Copyright Tim Littlefair 2016
# This work is licensed under the MIT License.
# https://opensource.org/licenses/MIT

"""
This module contains a base class which defines the framework for
extracting commit events from a log file output by a given VCS
command line tool, and subclasses which instantiate the framework
for the git and subversion VCS systems.
"""

import abc
import codecs
import datetime
import os
import re
import shutil
import stat
import sys
import subprocess
import tempfile

def workaround_python_issue26660(temp_dir_name):#pragma: no cover
    """Under Windows we need to work around https://bugs.python.org/issue26660

    Basically, cleanup fails on a directory created by
    tempfile.TemporaryDirectory() if there are any
    read-only files in the directory by the time it is
    cleaned up.  Both git and subversion create read-only
    files, so there will definitely be a problem.
    The fix is to delete everything under the temporary
    directory, but we can't delete the temp directory
    itself because cleanup expects to be allowed to do
    this."""
    def remove_readonly(func, path, _):
        "Clear the readonly bit and reattempt the removal"
        os.chmod(path, stat.S_IWRITE)
        func(path)
    for item in os.listdir(temp_dir_name):
        item_path = os.path.join(temp_dir_name, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path, onerror=remove_readonly)

class LogExtractorBase(metaclass=abc.ABCMeta):
    """Base class for extractors targetting different version control systems

    Subclasses need to retrieve a log from their target VCS and implement
    process_log_line so that it adds timed event entries from the retrieved
    log into the worklog object which is passed.
"""
    def __init__(self, stream):
        self.lines = stream.readlines()
        #self.process_log_line = LogExtractorBase.process_log_line
    @abc.abstractmethod
    def process_log_line(self, work_log, next_entry, line): #pragma: no cover
        """Purse virtual function which is overridden with the subclasses parser implementation"""
        pass
    @staticmethod
    def _exec(args, expected_stderr_regexes):
        subproc = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        subproc.stdin.close()
        ostream = codecs.getreader('UTF-8')(subproc.stdout)
        estream = codecs.getreader('UTF-8')(subproc.stderr)
        # We expect many lines on stdout, few or none on stderr
        # We read stdout to exhaustion before waiting for the
        # subprocess to exit, then we read stderr.
        # This seems to be the best way to avoid a deadlock
        # (but should we be extending to the complexity of a
        # threaded read?).
        stdout_lines = ostream.readlines()
        subproc.wait()
        stderr_lines = estream.readlines()
        subproc.stdout.close()
        subproc.stderr.close()
        estream.close()
        ostream.close()
        filtered_stderr_lines = []
        for line in stderr_lines:
            for regex in expected_stderr_regexes:
                if re.match(regex, line):
                    line = ''
                    break
            if len(line.strip()) == 0:
                continue
            else:
                filtered_stderr_lines += [line]
        if len(filtered_stderr_lines) > 0:
            unexpected_stderr_lines = '\n'.join(filtered_stderr_lines)
            raise RuntimeError("Unexpected output on standard error:\n" + unexpected_stderr_lines)
        retval = (subproc.returncode, stdout_lines, filtered_stderr_lines)
        return retval
    def feed(self, work_log):
        """Framework class which drives a log through a subclass's specific parser"""
        next_entry = [None, None, ""]
        for line in self.lines:
            next_entry = self.process_log_line(work_log, next_entry, line)
        # Process the trailing entry if it is meaningful
        if None not in next_entry:
            work_log.add_event(*next_entry[0:2])

# Constants used by GitLogExtractor
_GLE_COMMIT = "commit "
_GLE_AUTHOR = "Author: "
_GLE_AUTHOR_EMAIL_REGEX = re.compile(r"\s<.*>")
_GLE_DATE = "Date:   "
_GLE_STDERR_EXPECTED_REGEX = re.compile(r'Cloning into bare repository .*')
# Sample timestamp: 2016-09-11 09:31:24 +0800
_GLE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S %z"
class GitLogExtractor(LogExtractorBase):
    """Extractor targeting the git VCS"""
    def __init__(self, uri, stream=None):
        if stream:
            LogExtractorBase.__init__(self, stream)
        elif os.path.exists(uri):
            self._get_log_from_local_repo(uri)
        else:
            self._get_log_from_temp_repo(uri)
    def _get_log_from_temp_repo(self, url):
        with tempfile.TemporaryDirectory(suffix='.git') as temp_clone_dir:
            args = (
                'git', '--no-pager', 'clone', '--bare', '--no-checkout',
                url, temp_clone_dir
            )
            try:
                _, _, _ = LogExtractorBase._exec(args, [_GLE_STDERR_EXPECTED_REGEX])
            except RuntimeError:
                # A failed clone can delete the target sandbox directory, even
                # if it existed before the attempt, so we need to re-create it
                # to ensure that scope cleanup runs cleanly.
                if not os.path.exists(temp_clone_dir):
                    os.mkdir(temp_clone_dir)
                raise
            self._get_log_from_local_repo(temp_clone_dir)
            # On Windows, deletion of a git/svn sandbox on the cleanup
            # of the with structure can fail because there are read-only
            # files or directories within the .git or .svn directory.
            # The function below works around this by changing permissions
            # and deleting all subdirectories below the sandbox root.
            workaround_python_issue26660(temp_clone_dir)

    def _get_log_from_local_repo(self, git_dir_name):
        args = ('git', '--no-pager', '--git-dir=' + git_dir_name, "log", "--date=iso")
        _, self.lines, _ = LogExtractorBase._exec(args, [])
    def process_log_line(self, work_log, next_entry, line):
        line = line.strip()
        if line.startswith(_GLE_COMMIT):
            if None not in next_entry:
                work_log.add_event(*next_entry[0:2])
            next_entry = [None, None, ""]
        elif line.startswith(_GLE_AUTHOR):
            # Filter email addresses out to protect contributors from spam
            line = line.replace(_GLE_AUTHOR, "")
            line = re.sub(_GLE_AUTHOR_EMAIL_REGEX, "", line)
            next_entry[0] = line
        elif line.startswith(_GLE_DATE):
            next_entry[1] = datetime.datetime.strptime(
                line.replace(_GLE_DATE, ""), _GLE_TIME_FORMAT
            )
        elif not next_entry[2]:
            next_entry[2] = line
        else:
            next_entry[2] = " ".join((next_entry[2], line))
        return next_entry

# Constants used by SvnLogExtractor
_SLE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S %z"
class SvnLogExtractor(LogExtractorBase):
    """Extractor targeting the subversion VCS"""
    def __init__(self, uri, stream=None):
        if stream:
            LogExtractorBase.__init__(self, stream)
        else:
            self._get_log_from_repo(uri)
    def _get_log_from_repo(self, uri):
        args = ('svn', 'log', '-q', uri)
        _, self.lines, _ = LogExtractorBase._exec(args, [])
    def process_log_line(self, work_log, next_entry, line):
        line = line.strip()
        fields = line.split("|")
        if len(fields) == 3:
            next_entry[0] = fields[1].strip()
            next_entry[1] = datetime.datetime.strptime(fields[2][1:26], _SLE_TIME_FORMAT)
            work_log.add_event(*next_entry[0:2])
            next_entry = [None, None, ""]
        return next_entry

def args_to_extractors(args):
    """This function infers the extractor(s) which need to run from command line arguments

    The inference can be based on an explicit directive to use a particular VCS, or
    the URL of the repository to be processed, or the content of the repository if
    it is on the local filesystem.
    """
    extractors = []
    default_extractor_class = GitLogExtractor
    for arg in args:
        if arg == '--': #pragma: no cover
            extractors += [default_extractor_class(None, stream=sys.stdin)]
        elif arg == "--git":
            default_extractor_class = GitLogExtractor
        elif arg == "--svn":
            default_extractor_class = SvnLogExtractor
        elif arg.endswith(".git"):
            extractors += [GitLogExtractor(arg)]
        elif os.path.exists(os.path.join(arg, '.git')):
            extractors += [GitLogExtractor(os.path.join(arg, '.git'))]
        elif os.path.exists(os.path.join(arg, '.svn')):
            extractors += [SvnLogExtractor(arg)]
        elif os.path.exists(arg):
            raise RuntimeError("Unable to determine sandbox type")
        else:
            extractors += [default_extractor_class(arg)]
    return extractors
