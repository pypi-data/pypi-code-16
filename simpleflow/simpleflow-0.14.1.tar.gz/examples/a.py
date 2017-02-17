from __future__ import print_function

from simpleflow import Workflow, activity, canvas, futures
from simpleflow.task import ActivityTask


@activity.with_attributes(task_list='quickstart', version='example', idempotent=True)
class Delay(object):
    def __init__(self, indata):
        self.indata = indata

    def execute(self):
        print('IN Delay, indata:{}'.format(self.indata))
        self.indata = '{}...Delay'.format(self.indata)
        return self.indata


@activity.with_attributes(task_list='quickstart', version='example', idempotent=True)
class Foo(object):
    def __init__(self, indata):
        self.indata = indata

    def execute(self):
        print('IN Foo, indata:{}'.format(self.indata))
        self.indata = '{}...Foo'.format(self.indata)
        return self.indata


@activity.with_attributes(task_list='quickstart', version='example', idempotent=True)
class Bar(object):
    def __init__(self, indata):
        self.indata = indata

    def execute(self):
        print('IN Bar, indata:{}'.format(self.indata))
        self.indata = '{}...Bar'.format(self.indata)
        return self.indata


@activity.with_attributes(task_list='quickstart', version='example', idempotent=True)
class Boo(object):
    def __init__(self, indata):
        self.indata = indata

    def execute(self):
        print('IN Boo, indata:{}'.format(self.indata))
        self.indata = '{}...Boo'.format(self.indata)
        return self.indata


@activity.with_attributes(task_list='quickstart', version='example', idempotent=True)
class Moo(object):
    def __init__(self, indata):
        self.indata = indata

    def execute(self):
        print('IN Moo, indata:{}'.format(self.indata))
        self.indata = '{}...Moo'.format(self.indata)
        return self.indata


class MyWorkflow(Workflow):
    name = 'zz'
    version = 'example'
    task_list = 'example'

    def run(self):
        print('START!!!!')
        c1 = canvas.Chain(
            (Delay, 'Path least traveled'),
            Boo,
            Foo,
            Bar,
            send_result=True)
        c2 = canvas.Chain(
            (Delay, 'The easy way'),
            Foo,
            Moo,
            Bar,
            send_result=True)
        g = canvas.Group(c1, c2)
        # print(g)
        f = self.submit(g)
        futures.wait(f)
