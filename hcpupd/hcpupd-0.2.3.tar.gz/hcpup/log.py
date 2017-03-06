# The MIT License (MIT)
#
# Copyright (c) 2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import logging
from logging.handlers import RotatingFileHandler
from io import StringIO
from pprint import pprint

def dpprint(firstline, obj, printable=False):
    """
    Convert pprint() output into a long string, ready for logging.log().

    :param firstline:   the first line to log
    :param obj:         the object to log, indented starting at line 2
    :return:            the string to log
    """
    with StringIO() as tmphdl:
        print(firstline, file=tmphdl)
        if printable:
            print(obj, file=tmphdl)
        else:
            pprint(obj, stream=tmphdl)
        tmphdl.seek(0)
        with StringIO() as t2hdl:
            first = True
            for i in tmphdl.readlines():
                if first:
                    print(i, end='', file=t2hdl)
                    first = False
                else:
                    print('\t'+i, end='', file=t2hdl)
            return t2hdl.getvalue()


class BlockFilter(logging.Filter):
    """
    A class to block several sub-loggers.
    """
    def __init__(self, iblock, sblock, **kwds):
        """
        :param iblock:      a list of loggers to block explicitely
        :param sblock:      a list of loggers to block along with all children
        """
        super().__init__(**kwds)
        self.iblock = iblock
        self.sblock = sblock

    def filter(self, record):
        """
        This one filters out the recs to block.

        :param record:  the record to log
        :return:        zero if to block, else the record
        """
        if record.name in self.iblock:
           return 0

        if self.sblock:
            for i in self.sblock:
                if record.name.startswith(i):
                    return 0

        return record


def initlogging(logfile, debug, stdout=True):
    """
    Setup logging.

    :param logfile:     the logfile to write to
    :param debug:       True if debug is requested
    :return:            TimedRotatingFileHandler
    """

    # Enable logging to make sure we get messages from the daemon
    logger = logging.getLogger()
    if debug:
        ff = logging.Formatter('%(asctime)s %(levelname)s %(process)d '
                               '%(name)s(%(lineno)d): %(message)s',
                               # '%m/%d %H:%M:%S')
                               )
    else:
        ff = logging.Formatter('%(asctime)s %(levelname)s %(process)d: '
                               '%(message)s',
                               '%m/%d %H:%M:%S')
    fs = logging.Formatter('%(message)s')

    # block the warnings from pyinotify
    bf = BlockFilter(['pyinotify'], [])

    lf = RotatingFileHandler(logfile, mode='a', maxBytes=10240**2,
                             backupCount=9)
    lf.addFilter(bf)
    lf.setFormatter(ff)
    logger.addHandler(lf)

    if stdout:
        ls = logging.StreamHandler(stream=sys.stdout)
        ls.addFilter(bf)
        ls.setFormatter(fs if not debug else ff)
        logger.addHandler(ls)

    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    return lf.stream
