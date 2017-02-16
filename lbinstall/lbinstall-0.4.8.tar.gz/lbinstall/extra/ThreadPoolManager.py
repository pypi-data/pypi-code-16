import sys

try:
    from Queue import Queue
except:
    from queue import Queue
from threading import Thread


class Worker(Thread):
    def __init__(self, tasks, results):
        Thread.__init__(self)
        self.tasks = tasks
        self.results = results
        self.daemon = True
        self.start()

    def run(self):
        while True:
            kwd_mark = object()
            func, args, kargs = self.tasks.get()
            result = {
                'id': args + (kwd_mark,) + tuple(sorted(kargs.items())),
                'result': None,
                'success': False
            }
            try:
                return_val = func(*args, **kargs)
                result['result'] = return_val
                result['success'] = True
            except Exception as e:
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.results.put(result)
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        self.results = Queue()
        for _ in range(num_threads):
            Worker(self.tasks, self.results)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()

    def get_results(self):
        """ Return the pool results """
        self.wait_completion()
        results = []
        while not self.results.empty():
            cursor = self.results.get()
            if cursor is None:
                break
            results.append(cursor)
        return results
