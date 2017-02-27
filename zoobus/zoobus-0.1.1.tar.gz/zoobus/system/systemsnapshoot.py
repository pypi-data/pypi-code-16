#coding=utf8
"""system snapshoot. 
"""

# Fixture for division, int/int -> float
from __future__ import division

import datetime
import os
import socket
from optparse import OptionParser

from dateutil import parser

import zoobus.time
from zoobus.log.printlog import logprint


class SystemSnapshoot(object):
    def __init__(self, path, interval=None, verbose=False):
        self.interval = interval or 60
        self._init_log(path, verbose)

    def _init_log(self, path, verbose):
        self.print_mem, logger = logprint('memory', path, to_stdout=verbose)
        self.print_cpu, logger = logprint('cpu', path, to_stdout=verbose)
        self.print_avgload, self.LOG = logprint('load_average', path,
                                                to_stdout=verbose)

    def memory_state(self):
        f = os.popen('ps aux --sort=-rss')
        log = f.read()
        header = '='*35 + ' MEMORY ' + '='*35
        self.print_mem('\n' + header + '\n'+'\n'.join(log.split('\n')[:10]) + '\n')

    def cpu_state(self):
        f = os.popen('ps aux --sort=-pcpu')
        log = f.read()
        header = '='*35 + '  CPU   ' + '='*35
        self.print_cpu('\n' + header + '\n'+'\n'.join(log.split('\n')[:10]) + '\n')


    def load_average(self):
        f = os.popen('uptime')
        log = f.read()
        infos = log.split('average:')
        load_average = infos[-1]
        load_average = load_average.split(',')

        host = socket.gethostname()
        time = log[:8]
        srv_time = str(datetime.date.today()) + ' ' + zoobus.time
        srv_time = parser.parse(srv_time)

        la_1 = load_average[0]
        la_5 = load_average[1]
        la_15 = load_average[2]
        header = '='*35 + '  LOAD  ' + '='*35
        log = '\n%s\n%s' % (header, log) 
        self.print_avgload(log)


    def main(self):
        "entry point"
        while True:
            try:
                self.memory_state()
                self.cpu_state()
                self.load_average()
            except:
                self.LOG.exception(str(datetime.datetime.now()))

            zoobus.time.sleep(self.interval)

def main():
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", 
                      help="save file path", metavar="PATH")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="print to stdout")

    (options, args) = parser.parse_args()
    if not options.path:
        parser.error("need save path.")
    SystemSnapshoot(path=options.path, verbose=options.verbose).main()
