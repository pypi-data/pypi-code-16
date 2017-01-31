import functools
import asyncio

import concurrent.futures

import requests

from apslite_agent.config import get_config


def singleton(f):
    cache = [None]

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not cache[0]:
            cache[0] = f(*args, **kwargs)

        return cache[0]

    return wrapper


@singleton
def get_agent_version():
    try:
        import pkg_resources

        return pkg_resources.get_distribution('apslite_agent').version
    except:
        return 'master'


def check(result, expect):
    statuses = []

    if not isinstance(expect, list):
        expect = [expect]

    for item in expect:
        status = False

        for key, value in item.items():
            status = result[key] == value

            if not status:
                break

        statuses.append(status)

    return any(statuses)


@singleton
def get_executor():
    max_workers = get_config().get('max_worker_threads')
    return concurrent.futures.ThreadPoolExecutor(max_workers)


async def request(*args, **kwargs):
    def req():
        return requests.request(*args, **kwargs)

    executor = get_executor()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, req)
