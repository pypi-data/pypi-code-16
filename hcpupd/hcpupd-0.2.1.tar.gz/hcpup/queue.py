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

import logging
import time
from queue import PriorityQueue, Empty
from threading import Thread, Lock

class Queues(Thread):
    """
    A class holding all queues and locks.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger(__name__ + '.Queues')

        self.queue = PriorityQueue()       # upload queue
        self.rvqueue = PriorityQueue()     # recovery queue
        self.timerqueue = PriorityQueue()  # used to stop this thread

        self.ddict = {}      # to overcome multiple CREATE events for dirs
        self.rvdict = {}     # the recovery dict
        self.dcdict = {}     # the diskcrawler dict
        self.rvlock = Lock() # lock for rvdict

        self.watchmgr = None  # inotify watchma

        self.logger.debug('initialized queues and locks')

    def run(self):
        """
        Run the uploader thread.
        """
        self.logger.debug('{} started'.format(self.name))

        try:
            while True:
                try:
                    prio, item = self.timerqueue.get(block=True, timeout=5)
                except Empty:
                    with self.rvlock:
                        t = time.time()
                        c1 = 0
                        tmp = tuple(self.ddict.keys())
                        for i in tmp:
                            if t - self.ddict[i] > 10:
                                del self.ddict[i]
                                c1 += 1
                    if c1:
                        self.logger.debug('purged {} entries from ddict'
                                          .format(c1))
                    continue
                else:
                    self.timerqueue.task_done()

                if item == '!**exit**!':
                    self.logger.debug('{} exiting'.format(self.name))
                    break

        except Exception:
            self.logger.exception('{} crashed!'.format(self.name))
