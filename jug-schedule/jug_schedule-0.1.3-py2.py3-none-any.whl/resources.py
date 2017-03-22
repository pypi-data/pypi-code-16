# -*- coding: utf-8 -*-

import json
from jug.task import TaskGenerator

__all__ = [
    "ResourcesTaskGenerator",
]

VALID_PARAMS = ("cpu", "mem", "queue")


def encode_resources(name, resources):
    return "{0} {1}".format(name, json.dumps(resources))


def decode_resources(target):
    if ' ' not in target:
        return {}
    else:
        return json.loads(target.split(' ', 1)[1])


class _WrapTaskGenerator(TaskGenerator):
    def __call__(self, *args, **kwargs):
        task = super(_WrapTaskGenerator, self).__call__(*args, **kwargs)
        task.name = encode_resources(task.name, self._resources)
        return task


def ResourcesTaskGenerator(**resources):
    """
    @ResourcesTaskGenerator(cpu=10, mem=100)
    def f(arg0, arg1, ...)
        ...

    Behaves the same as jug's TaskGenerator but allows specifying resources
    which will then be used by the scheduler to request then to the queueing
    system.

    Current list of supported arguments ::

        cpu   = Number of cpu cores/threads to allocate
        mem   = Maximum memory necessary (in MB)
        queue = Name of queue to use

    All of the above are optional.

    Also note that these arguments are ignored if running with 'jug execute'.
    They are only relevant when using 'jug schedule'
    """
    for key in resources:
        assert key in VALID_PARAMS, "Invalid argument given {0}".format(key)

    def task_generator_wrapper(f):
        task_generator = _WrapTaskGenerator(f)
        task_generator._resources = resources
        return task_generator

    return task_generator_wrapper


# vim: ai sts=4 et sw=4
