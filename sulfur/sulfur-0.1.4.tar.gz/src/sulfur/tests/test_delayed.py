import pytest

from sulfur.all import server
from sulfur.delayed import Delayed
from sulfur.testserver import TestServer as Server


class Foo:
    def __repr__(self):
        return 'foo'

    def __init__(self, *args):
        self.args = args

    def __del__(self):
        del self.args


@pytest.fixture
def delayed():
    return Delayed(Foo)


def test_delayed_object_example():
    assert str(server).startswith('<sulfur.testserver.TestServer object')
    assert isinstance(server, Server)
    assert not isinstance(server, Delayed)
    assert hasattr(server, 'start')
    assert hasattr(server, 'stop')


def test_delayed_methods(delayed):
    assert str(delayed) == 'foo'
    assert isinstance(delayed, Foo)
