from Queue import Queue
from threading import Thread


'''
    Apply a lambda function to a list of input //
    threadpool = Pool(worker=N, func=LambdaFunc), create a pool of N threads
    threadpool.load(inputArray), load the list of inputs



'''


def map(array, callback, worker=2, verbose=False):
    pool = lambdaPool(worker=worker, func=callback, verbose=verbose)
    pool.load(array)
    x = pool.start()
    return x


class lambdaPool(object):

    def worker(self):
        while True:
            _i = len(self.outputs) - self.q.qsize()
            e = self.q.get()
            if self.verbose:
                print("I got " + e +" from queue its output index is " + str(_i))
            self.outputs[_i] = self.func(e)
            self.q.task_done()

    def __init__(self, worker = 2, func=None, verbose=False):
        self.nbWorker = worker
        self.q = Queue()
        self.func = func
        self.verbose = verbose

    def load(self, taskList):
        self.outputs = [ None for x in taskList ]
        for t in taskList:
            self.q.put(t)
    def start(self):
        if self.verbose:
            print '*** Main thread starting ' + str(self.q.qsize())
        for i in range(self.nbWorker):
            self.t = Thread(target=self.worker)
            self.t.daemon = True
            self.t.start()
        if self.verbose:
            print '*** Main thread waiting ' + str(self.q.qsize())
        self.q.join()
        if self.verbose:
            print '*** Done'
        return self.outputs
