import functools
import json
import logging
import pkgutil

import asyncio

from apslite_agent import constants

logger = logging.getLogger(__name__)


def json_result(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return json.dumps(f(*args, **kwargs))

    return wrapper


def get_task(name, **kwargs):
    loader = pkgutil.get_loader('{}.{}'.format(constants.TASKS_MODULE, name))
    task_not_found = "Unknown task: {}".format(name)

    if loader is None:
        raise RuntimeError(task_not_found)

    module = loader.load_module()

    factory = getattr(module, 'task_factory')

    if callable(factory):
        m = factory(**kwargs)

        if name in m:
            return m[name]

    raise RuntimeError(task_not_found)


@asyncio.coroutine
def parse_params_and_run_task(task_name, params, **kwargs):
    task = task_name.split('.')[0]
    result = {
        'type': 'task_result',
        'status': 'error',
    }

    try:
        run_task = get_task(task, **kwargs)
    except Exception as e:
        result['message'] = str(e)
        return result

    try:
        task_data = params or {}
    except ValueError:
        result['message'] = "Invalid request format"
        return result

    logger.info("Running task %s", task_name)

    params = task_data.get('params')
    result = yield from run_task(params)
    result['task'] = task_name

    logger.debug("Task %s returned %s", task_name, result)

    return result
