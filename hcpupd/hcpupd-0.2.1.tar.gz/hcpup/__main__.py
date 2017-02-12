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
from os import chmod, getcwd, getuid
from pwd import getpwuid
from shutil import rmtree
import signal
import daemon
import logging
from stat import S_IREAD, S_IWRITE, S_IEXEC
from threading import Event

import hcpup

NOTIFIER = None
SHUTDOWNEVENT = Event()

def main():
    global NOTIFIER

    # get the command line arguments
    opts = hcpup.parseargs()

    # read the configuration file
    try:
        conf = hcpup.conf.readconf(opts.configfile)
    except Exception as e:
        sys.exit(e)

    # Enable logging to make sure we get messages from the daemon
    try:
        fh = hcpup.log.initlogging(conf['logfile'], conf['debug'],
                        stdout=False if opts.daemon else True)
    except Exception as e:
        sys.exit('Fatal: can\'t initialize logging...\n\thint: {}'.format(e))
    logger = logging.getLogger(__name__+'.main')

    logger.debug('hcpupd startet by user {}'.format(getpwuid(getuid())[0]))

    cc = conf.copy()
    cc['password'] = '*'*8
    logger.debug(hcpup.log.dpprint('Configuration file content was '
                         'read as this:', cc))
    del cc

    # Turn ourselves into a daemon unless otherwise requested
    if opts.daemon:
        logger.debug('hcpupd is requested to run in daemon mode...')

        # To make sure that we don't lose the required binaries in case we run
        # in an environment where the tool has been bundled by
        # pyinstaller -F hcpbench.py, we need to take care that the temp folder
        # holding the binaries can't be deleted by the pyinstaller bootcode.
        if hasattr(sys, '_MEIPASS') and sys._MEIPASS.startswith('/tmp'):
            chmod(sys._MEIPASS, S_IREAD | S_IEXEC)
            logger.debug('sys._MEIPASS ({}) set to r/o'.format(sys._MEIPASS))

        try:
            dae = daemon.DaemonContext(files_preserve=[fh],
                                       signal_map={signal.SIGINT: signalhandler,
                                                   signal.SIGTERM: signalhandler},
                                       working_directory=getcwd(),
                                       prevent_core=True)
        except Exception as e:
            logger.exception('creation of DaemonContext failed...\n\thint: {}'
                             .format(e))
            sys.exit(1)
        logger.debug('DaemonContext initialized: {}'.format(dae))

        try:
            dae.open()
        except Exception as e:
            logger.exception('dae.open() failed...\n\thint: {}'.format(e))
            sys.exit(1)
        logger.debug('hcpupd enters daemon mode')
        logger.debug('_MEIPASS in sys.__dict__: {}'.format(hasattr(sys, '_MEIPASS')))
        logger.debug('sys._MEIPASS: {}'.format(sys._MEIPASS))

        if hasattr(sys, '_MEIPASS') and sys._MEIPASS.startswith('/tmp'):
            try:
                chmod(sys._MEIPASS, S_IREAD | S_IWRITE | S_IEXEC)
            except Exception as e:
                logger.exception('chmod(_MEIPASS) failed - {}'.format(e))
            logger.debug('sys._MEIPASS ({}) set to r/w'.format(sys._MEIPASS))
    else:
        logger.info('hcpupd is running in foreground')
        signal.signal(signal.SIGINT, signalhandler)
        signal.signal(signal.SIGTERM, signalhandler)

    # Prepare the connection to HCP
    try:
        target = hcpup.up.createtarget(conf)
    except Exception as e:
        logger.error('Fatal: connection to "{}" failed\n\thint: {}'
                     .format(conf['namespace'], e))
        sys.exit(1)

    # Start the background threads
    uwts = hcpup.up.startuploaders(conf, target)

    try:
        NOTIFIER = hcpup.notify.Notify(conf['watchdir'], uwts[0])
        # make the watchmanager object available for use by uploaders
        uwts[0].watchmgr = NOTIFIER.wm
    except Exception as e:
        sys.exit('Fatal: error while calling inotify\n\thint: {}'.format(e))

    # if requested, schedule existing files for upload
    if conf['upload existing files']:
        NOTIFIER.scheduleexisting()

    # wait until the process has been forced to stop by SIGINT or SIGTERM
    SHUTDOWNEVENT.wait()

    # shutdown handling
    NOTIFIER.stop()
    for i in uwts:
        logger.debug('sending EXIT command to {}'.format(i.name))
        if i.name.startswith('uploader'):
            uwts[0].queue.put((1, '!**exit**!'))
        elif i.name.startswith('dircrawler'):
            uwts[0].rvqueue.put((1, '!**exit**!'))
        elif i.name.startswith('queues'):
            uwts[0].timerqueue.put((1, '!**exit**!'))

    for t in uwts:
        logger.debug('joining thread {}'.format(t.name))
        t.join()

    if hasattr(sys, '_MEIPASS') and sys._MEIPASS.startswith('/tmp'):
        logger.debug('removing sys._MEIPASS ({})'.format(sys._MEIPASS))
        rmtree(sys._MEIPASS, ignore_errors=True)
    logger.info('==> we\'re done now <==')


def signalhandler(signum, frame):
    """
    Signal handler used when running as a daemon to catch SIGINT and close.
    :param signum:  the signal
    :param frame:   a frame
    :return:
    """
    if not SHUTDOWNEVENT.is_set():
        logger = logging.getLogger(__name__+'.signalhandler')
        logger.debug('received signal {} - forced ending, immediately'
                    .format(signum))
        SHUTDOWNEVENT.set()


