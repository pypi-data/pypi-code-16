"""
SQS-Task

It's a message queue for job execution using AWS SQS

It put data in 2 queues:
    - queued
    - completed
    - failed

queued: messages contain runnable messages, ie: function to run for task

completed: contains completed data

failed: will contained the finished results which will contain completed
            or failed data


taskq = TaskQ("myQname", "***", "***")

- To add a task(job)
taskq.add(my_function_name, *args, **args)

You can also use the decorator

@taskq.task
def fn(a, b, c):
    pass

- To process jobs

myQ.run_daemon()

- To received finished data

def callback(data):
    # do something with data

# myQ.run_finished(callback)

Once captured, it will delete the message from the queue

"""

import datetime
import time
import logging
import functools
from pickle import dumps, loads
from boto import sqs

QUEUED_POOL = "queued"
COMPLETED_POOL = "completed"
FAILED_POOL = "failed"


class TaskQ(object):
    _pool = {}

    def __init__(self,
                 name,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 region='us-east-1',
                 visibility_timeout=None
                 ):
        """
        :param name: the name of the messages container. From that name it will create queued and finished pools
        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param region:
        :param visibility_timeout: The default visibility timeout for all messages written in the queue. This can be overridden on a per-message.
        :return:
        """
        self.name = name
        self.visibility_timeout = visibility_timeout

        self.connect(region=region,
                     aws_access_key_id=aws_access_key_id,
                     aws_secret_access_key=aws_secret_access_key)

    def connect(self, aws_access_key_id=None, aws_secret_access_key=None, region='us-east-1'):
        """
        Create a connection
        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param region:
        :return:
        """
        self.conn = sqs.connect_to_region(region=region,
                                          aws_access_key_id=aws_access_key_id,
                                          aws_secret_access_key=aws_secret_access_key)

    def task(self, **kw):
        """
        A decorator to `add` function to the queue
        :param kw: future proof placeholder
        :return:
        """

        def deco(fn):
            @functools.wraps(fn)
            def rator(*args, **kwargs):
                self.add(callback=fn, *args, **kwargs)

            return rator

        return deco

    def add(self, callback, delay_seconds=None, *args, **kwargs):
        """
        To add a task to the queue
        :param callback: a callback function
        :param delay_seconds: Number of seconds (0 - 900) to delay this message from being processed.
        :param args: args to pass back in the callable
        :param kwargs:
        :return: the message id
        """
        m = self.write_message(QUEUED_POOL,
                               delay_seconds=delay_seconds,
                               data={
                                   'callback': callback,
                                   'args': args,
                                   'kwargs': kwargs
                               })
        return m.id

    def fetch(self, pool_key=QUEUED_POOL, size=5, wait_time=30):
        """
        Retrieve the message
        :param pool_key: the pool to retrieve the message from
        :param size: the total of messages to fetch
        :param wait_time:
        :return: generator
        """
        q = self.queue(pool_key)
        while q.count():
            for message in q.get_messages(num_messages=size,
                                          wait_time_seconds=wait_time):
                yield message

    def queue(self, pool_key=QUEUED_POOL):
        if pool_key not in self._pool:
            name = "%s-%s" % (self.name, pool_key)
            queue = self.conn.get_queue(name)
            if not queue:
                queue = self.conn.create_queue(name,
                                               visibility_timeout=self.visibility_timeout)
            self._pool[pool_key] = queue
        return self._pool.get(pool_key)

    def write_message(self, pool_key, data, delay_seconds=None):
        """
        Write the message to the pool
        :param pool_key: The pool key
        :param data: the data to save
        :param delay_seconds: Number of seconds (0 - 900) to delay this message from being processed.
        :return:
        """
        message = sqs.message.Message(body=dumps(data))
        return self.queue(pool_key).write(message, delay_seconds=delay_seconds)

    def read_message(self, message):
        """
        :param message: sqs.message.Message
        :return: 
        """
        return loads(message.get_body())

    def process(self, pool_key, callback, size=5, pause=5, burst=False,
                wait_time=20, delete=True):
        """
        To process a pool
        :param pool_key: 
        :param callback: A callback function
        :param size: 
        :param pause: 
        :param burst: 
        :param wait_time: 
        :param delete: 
        :return: 
        """

        while True:
            for message in self.fetch(pool_key=pool_key,
                                      size=size,
                                      wait_time=wait_time):
                body = self.read_message(message)
                callback(self, body=body)
                if delete:
                    message.delete()

            if burst:
                break
            time.sleep(pause)

    def run(self, size=5, pause=5, burst=False,
            wait_time=20, write_failed=True):
        """
        Run the task worker
        :param size: Total of tasks to request at a time
        :param pause: The pause time between each request
        :param burst: If true, it will run once
        :param wait_time: wait time between
        :param write_failed: To write failed
        :return:
        """

        while True:
            for message in self.fetch(pool_key=QUEUED_POOL,
                                      size=size,
                                      wait_time=wait_time):
                fail = False
                data = {
                    "id": message.id,
                    "status": "pending",
                    "created_at": datetime.datetime.now()
                }
                try:
                    body = self.read_message(message)
                    data.update({
                        "callback": body.get("callback"),
                        "args": body.get("args"),
                        "kwargs": body.get("kwargs")
                    })

                    callback = body.get("callback")
                    result = callback(*body.get("args"), **body.get("kwargs"))
                    data.update({
                        "status": "completed",
                        "result": result,
                    })
                except Exception as ex:
                    fail = True
                    data.update({
                        "status": "failed",
                        "message": ex.message
                    })
                    logging.error("Failed running task: '%s'" % ex.message)
                finally:
                    if not fail:
                        self.write_message(COMPLETED_POOL, data)
                    elif write_failed:
                        self.write_message(FAILED_POOL, data)

                message.delete()
            if burst:
                break
            time.sleep(pause)

    def _run_queued(self, task, body):

        try:
            cb = body.get("callback")
            args = body.get("args")
            kwargs = body.get("kwargs")
        except Exception as ex:
            pass

    def run_queued(self, **kw):
        self.process(QUEUED_POOL, callback=self._run_queued, **kw)

    def run_completed(self, callback, **kw):
        self.process(COMPLETED_POOL, callback=callback, **kw)

    def run_failed(self, callback, **kw):
        self.process(FAILED_POOL, callback=callback, **kw)

    def purge(self, pool_key):
        """
        Purge message in this queue
        :param pool_key:
        :return:
        """
        q = self._pool.get(pool_key)
        if q:
            q.purge()

    def delete(self, pool_key):
        """
        To delete a queue
        :param pool_key:
        :return:
        """
        q = self._pool.get(pool_key)
        if q:
            q.delete()

    def delete_all(self):
        """
        Delete all queues
        :return:
        """
        for k, q in self._pool.items():
            q.delete()

    def purge_all(self):
        """
        Purge messages from all queues
        :return:
        """
        for k, q in self._pool.items():
            q.purge()
