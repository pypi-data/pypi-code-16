import os
import random

import pytest

from sulfur.tests.utils import get_source


@pytest.fixture(scope='session')
def server_path():
    return os.path.join(os.path.dirname(__file__), 'data')


@pytest.yield_fixture(scope='session')
def server(server_path, port):
    from sulfur.testserver import TestServer

    server = TestServer(path=server_path, port=port)
    server.start()
    yield server
    server.stop()


@pytest.fixture(scope='session')
def server_url(server):
    return server.base_url


@pytest.fixture(scope='session')
def port():
    return random.randint(8001, 65000)


@pytest.fixture(scope='session')
def driver_type():
    # return 'chrome'
    return 'phantomjs'


@pytest.yield_fixture
@pytest.mark.usefixtures('server')
def driver(driver_type, server_url):
    from sulfur import Driver

    driver = Driver(driver_type, home=server_url)
    yield driver
    driver.close(quit=True)


@pytest.fixture
def another_source():
    return get_source('another.html')


@pytest.fixture
def bad_source():
    return get_source('bad.html')


@pytest.fixture
def base_source():
    return get_source('base.html')


@pytest.fixture
def other_source():
    return get_source('other.html')
