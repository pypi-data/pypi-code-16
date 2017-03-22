"""
This module defines APIs for multitasking and queueing
"""

from __future__ import print_function
# http://stackoverflow.com/a/2740494
# http://stackoverflow.com/a/6319267
# http://stackoverflow.com/a/15144765

from future import standard_library
standard_library.install_aliases()
#from builtins import str
from builtins import range
from builtins import object
import multiprocessing
import multiprocessing.dummy
import functools
try:
    import threading as threading
except ImportError:
    import dummy_threading as threading  # ensures threading exists
import queue
from time import time as _time
from multiprocessing.managers import SyncManager
from advutils import BaseCreation
# http://stackoverflow.com/a/33764672/5288758
# https://pymotw.com/3/multiprocessing/communication.html
from itertools import count

Empty = queue.Empty


class MultiProcessingAPI(object):
    """
    Class to unify Multi processing and threading
    """

    def __init__(self, spawn=False):
        self.spawn = spawn

    def Process(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        if self.spawn:  # creates new python process
            return multiprocessing.Process(*args, **kwargs)
        else:  # creates new thread
            return threading.Thread(*args, **kwargs)

    Thread = Process

    def Pool(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        if self.spawn:
            return multiprocessing.Pool(*args, **kwargs)
        else:
            return multiprocessing.dummy.Pool(*args, **kwargs)

    ################################################
    def Queue(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        if self.spawn:  # creates new python process
            return multiprocessing.Queue(*args, **kwargs)
        else:  # creates new thread
            return queue.Queue(*args, **kwargs)

    def Event(self):
        """

        :return:
        """
        if self.spawn:  # creates new python process
            return multiprocessing.Event()
        else:  # creates new thread
            return threading.Event()

    def Semaphore(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        if self.spawn:  # creates new python process
            return multiprocessing.Semaphore(*args, **kwargs)
        else:  # creates new thread
            return threading.Semaphore(*args, **kwargs)

    def Lock(self):
        """

        :return:
        """
        if self.spawn:  # creates new python process
            return multiprocessing.Lock()
        else:  # creates new thread
            return threading.Lock()

    def RLock(self):
        """

        :return:
        """
        if self.spawn:  # creates new python process
            return multiprocessing.RLock()
        else:  # creates new thread
            return threading.RLock()

    ################################################
    def decorate(self, obj):
        """

        :param obj:
        :return:
        """
        @functools.wraps(obj)
        def dd(*args, **kwargs):
            return self.manage(obj, *args, **kwargs)
        return dd

    def manage(self, obj, *args, **kwargs):
        """

        :param obj:
        :param args:
        :param kwargs:
        :return:
        """
        if self.spawn:  # manage if in process
            SyncManager.register('temp', obj)
            a = SyncManager()
            a.start()
            return a.temp(*args, **kwargs)
        return obj(*args, **kwargs)


api = MultiProcessingAPI()  # adds a global manager


def heappush(l, item):
    """
    Append to queue with priority (where carriers are organized from
    smaller to biggest)

    :param l: list queue
    :param item: Event
    """
    # TODO see if this method is in queue package and select better
    for pos, i in enumerate(l):
        if item >= i:
            l.insert(pos, item)
            return

    l.append(item)


def heappop(l):
    """
    Consume last item from queue list (biggest carrier)

    :param l: list queue
    :return: last item from list
    """
    return l.pop()


class PriorityQueue(queue.PriorityQueue):
    """
    Variant of Queue.PriorityQueue in that FIFO rule is kept inside
    the same priority number groups.

    Entries are typically tuples of the form:  (priority number, data).
    """

    def _init(self, maxsize):
        self.queue = api.manage(list)

    def _put(self, item, heappush=heappush):
        heappush(self.queue, item)

    def _get(self, heappop=heappop):
        return heappop(self.queue)


class Designator(queue.PriorityQueue):
    """
    Task Designator with priority queue
    """

    def _init(self, maxsize):
        """

        :param maxsize:
        :return:
        """
        self.queue = api.manage(list)
        self._isOpen = True

    def _put(self, item, heappush=heappush):
        """

        :param item:
        :param heappush:
        :return:
        """
        if self._isOpen:
            heappush(self.queue, item)
        else:
            raise Exception("Queue is closed")

    def _get(self, heappop=heappop):
        """

        :param heappop:
        :return:
        """
        return heappop(self.queue)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """
        self.not_empty.acquire()
        try:
            if not block or not self._isOpen:  # do not block when closed
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while self._isOpen and not self._qsize():
                    self.not_empty.wait()
                if not self._isOpen and not self._qsize():
                    # Exception("While waiting empty Queue it was closed")
                    raise Empty
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = _time() + timeout
                while not self._qsize():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            return item
        finally:
            self.not_empty.release()

    def close(self):
        """

        :return:
        """
        self._isOpen = False
        self.not_empty.acquire()
        self.not_empty.notifyAll()
        self.not_empty.release()

    def isOpen(self):
        """

        :return:
        """
        return self._isOpen

    def __iter__(self):
        self.mutex.acquire()
        queue = self.queue
        for i in range(len(queue) - 1, -1, -1):
            yield queue[i]
        self.mutex.release()

    def __getitem__(self, index):
        return self.queue[index]

    def __setitem__(self, index, value):
        self.queue[index] = value

    def __delitem__(self, index):
        del self.queue[index]

    def __len__(self):
        return len(self.queue)


HIGHEST_PRIORITY = float("Inf")  # highest priority for QueueCarrier
LOWEST_PRIORITY = float("-Inf")  # lowest priority for QueueCarrier


@functools.total_ordering  # adds ordering and priority capabilities
class QueueCarrier(BaseCreation):
    """
    Base class Carrier used to convey data reliably in PriorityQueues
    """
    HIGHEST_PRIORITY = HIGHEST_PRIORITY
    LOWEST_PRIORITY = LOWEST_PRIORITY

    def __init__(self, priority):
        super(QueueCarrier, self).__init__()
        self.priority = priority

    # def __cmp__(self, other): # deleted in python 3, replaced for __eq__ and __lt__
    #    return cmp(self.priority, other.priority)

    def __eq__(self, other):  # complement with functools.total_ordering
        # priority comparison
        # return (self.priority,self.creation) == (other.priority,other.creation)
        # equality comparison
        return id(self) == id(other)

    def __lt__(self, other):  # complement with functools.total_ordering
        # priority comparison
        # if A is created first than B then A is expected to be less than B
        return (
            self.priority,
            self.creation_time) < (
            other.priority,
            other.creation_time)
        # return (self.priority,self._creation_order) < (other.priority,other._creation_order)
        # return (self.priority,) < (other.priority,)


class IterDecouple(object):
    """
    Decouple iterator from main thread and with processes.
    """

    def __init__(self, iterable, processes=None, buffsize=0, handler=None):
        """
        Get values from an iterable in a different thread. if the process that uses
        the items from the iterator is busy it keeps buffering values until they
        are requested. It enhances performance by reducing the waiting time taken
        by the retrieving items from an iterator used in the for loop.

            # given the following iterable
            iterable = not_processed_data() # e.g. generator

            # problem case: process that wastes idle time
            for i in iterable: # retrieving item from iterable takes time
                busy_process(i) # idle time to retrieve next i item

            # Usage: reduces wasted time by decoupling
            for i in decoupled_for(iterable): # for has been decoupled from iterable
                busy_process(i) # meanwhile next i items are been retrieved

        :param iterable: any object usable in a for loop
        :param processes: Number of processes to spawn
        :param buffsize: size of buffer to retrieve items ahead
        :param handler: handle function to process item from iterable
            and generate data. Notice that processing times from handler
            functions are detached from main.
        :param spawn: True to create new process, False to create new Thread
            Note: processes only support pickable objects.
        """
        self.iterable = iterable
        self.processes = processes
        self.call_func = handler
        self.buffsize = buffsize

        # Initialize variables
        self.queue = None
        self._finish_signal = None
        self.thread = None
        self._running = None  # knows it has never been initialized if None

    def start(self):
        """
        Start generating data from self.iterable
        to be consumable from self.queue
        """
        if self._running is True:
            raise Exception("Already running")

        def worker(queue, iterable):

            if self.processes is not None and self.call_func is not None:
                # call call_func inside processes and
                # synchronously put results into queue

                def process_func(previous_lock, next_lock, id, data):

                    def stop_func(force=False):
                        """
                        function to clean up locks and processes
                        :param force: force to clean and notify to close.
                        :return: True to close else False
                        """
                        if self._running and not force:
                            return False  # do not finish

                        if id is not None:
                            del processes_memo[id]  # release this process
                        next_lock.release()  # release for next task
                        # by releasing next task they can finish
                        # without putting data in queue
                        return True  # it can finish before starting to put data

                    if stop_func():  # close if iteration stopped
                        return

                    # process data
                    value = self.call_func(data)

                    # wait previous answers
                    if previous_lock is not None:
                        previous_lock.acquire()

                    if stop_func():  # close if iteration stopped
                        return

                    # put answer after previous answers
                    queue.put(value)
                    stop_func(force=True)  # clean up

                # initialize variables
                it = iter(iterable)
                processes_memo = {}  # list of processes

                # start first task
                previous_lock = api.Lock()
                previous_lock.acquire()
                id_time = _time()  # create id of process
                p = api.Process(target=process_func, args=(
                    None, previous_lock, id_time, next(it)))
                processes_memo[id_time] = p
                p.start()

                # keep filling processes with tasks
                while True:
                    if not self._running:
                        # execute just this routine
                        if len(processes_memo) == 0:
                            break  # ensures all processes are finished
                        else:
                            continue
                    try:
                        # fill processes with tasks
                        while len(processes_memo) < self.processes:
                            next_lock = api.Lock()
                            next_lock.acquire()
                            id_time = _time()
                            p = api.Process(target=process_func, args=(
                                previous_lock, next_lock, id_time, next(it)))
                            processes_memo[id_time] = p
                            p.start()
                            # update lock for next task
                            previous_lock = next_lock
                    except StopIteration:
                        if len(processes_memo) == 0:
                            break
            elif self.call_func is not None:
                # call call_func and put into queue
                for i in iterable:
                    if not self._running:
                        break  # it can finish before starting to put data
                    queue.put(self.call_func(i))
            else:
                # just place values into queue
                for i in iterable:
                    if not self._running:
                        break  # it can finish before starting to put data
                    queue.put(i)  # put data into queue

            self._finish_signal.set()  # decoupled for is finished

        self.queue = queue = api.Queue(
            self.buffsize)  # gets values from worker
        self._finish_signal = sig = api.Event()  # handles finishing signal
        self.thread = thread = threading.Thread(target=worker,
                                                args=(queue, self.iterable))
        self._running = True
        thread.start()

    def close(self):
        self._running = False

    def join(self):
        """
        Wait until data is generated and consumed from self.iterable
        """
        if not self._running:
            raise Exception("Not running")

        self.thread.join()
        self._running = False

    def __iter__(self):
        """
        Iterate over detached data from self.iterable
        """
        if not self._running:
            # start if not running
            self.start()
        return self

    def generator(self):
        """
        Generate detached data from self.iterable
        """
        while True:

            if self.queue.empty():
                # if tasks are done and queue was consumed then break
                if self._finish_signal.is_set() and self.queue.empty():
                    break
            else:
                # do not read if queue is empty
                value = self.queue.get()
                self.queue.task_done()
                yield value

        if self._running:
            self.join()

    def __next__(self):
        for i in self.generator():
            return i
        raise StopIteration

    next = __next__  # compatibility with python 2


def use_pool(func, iterable, workers=4, chunksize=1):
    """
    Map function over iterable using workers.

    :param func: function to use in processing
    :param iterable: iterable object
    :param workers: number of workers
    :param chunksize: number of chunks to process per thread
    :return:
    """
    pool = api.Pool(workers)  # Make the Pool of workers
    return pool.imap(func, iterable, chunksize)
