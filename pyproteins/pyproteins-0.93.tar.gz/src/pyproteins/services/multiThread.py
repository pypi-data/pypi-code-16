from Queue import Queue
from threading import Thread


'''
    Apply a lambda function to a list of input //
    threadpool = Pool(worker=N, func=LambdaFunc), create a pool of N threads
    threadpool.load(inputArray), load the list of inputs



'''


def map(array, callback, worker=2):
    pool = lambdaPool(worker=worker, func=callback)
    pool.load(array)
    x = pool.start()
    return x


class lambdaPool(object):

    def worker(self):
        while True:
            _i = len(self.outputs) - self.q.qsize()
            e = self.q.get()
            print("I got " + e +" from queue its output index is " + str(_i))
            #self.append(self.func(e))
            self.outputs[_i] = self.func(e)
            self.q.task_done()

    def __init__(self, worker = 2, func=None):
        self.nbWorker = worker
        self.q = Queue()
        self.func = func

    def load(self, taskList):
        self.outputs = [ None for x in taskList ]
        for t in taskList:
            self.q.put(t)
    def start(self):
        print '*** Main thread starting ' + str(self.q.qsize())
        for i in range(self.nbWorker):
            self.t = Thread(target=self.worker)
            self.t.daemon = True
            self.t.start()

        print '*** Main thread waiting ' + str(self.q.qsize())
        self.q.join()
        print '*** Done'
        return self.outputs
