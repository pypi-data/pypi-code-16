#! python3
# encoding: utf-8

# Copyright Tim Littlefair 2016
# This work is licensed under the MIT License.
# https://opensource.org/licenses/MIT

"""
This package defines a framework which can be used to extract
the timestamps of commit events from a version control system
(VCS) log, and convert this into an inference about continuous
time spent on the code.
"""
import os.path
import sys

from .extractors import LogExtractorBase, GitLogExtractor, SvnLogExtractor, args_to_extractors
from .extractors import workaround_python_issue26660
from .worklog import WorkDayEntry, WorkLog, Assumptions

USAGE = """
Usage: 
git { --git-dir=<wherever> } log --date=iso | %s --
    Generate a work log from the generated git log stream
    based on some assumptions about how long before and
    after each commit developers would have been working.
"""

def command_line_interface(args, ostream):
    """The command line interface for the package"""
    work_log = WorkLog()
    for extractor in args_to_extractors(args):
        extractor.feed(work_log)
    work_log.report(ostream)

def main():#pragma: no cover
    """Entry point if the script is run by name"""
    if len(sys.argv) < 2:
        print(USAGE%(os.path.basename(sys.argv[0]),))
    else:
        try:
            command_line_interface(sys.argv[1:], sys.stdout)
        except RuntimeError as rte:
            print(str(rte), file=sys.stderr)

if __name__ == "__main__": #pragma: no cover
    main()
