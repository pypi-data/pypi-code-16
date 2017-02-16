import os
import signal

import pytest

import kube
import kube._testing


@pytest.hookimpl
def pytest_addoption(parser):
    parser.addoption(
        '--verify',
        action='store',
        type=str,
        help='Verify tests against real cluster using given kubectl context',
    )


@pytest.fixture(scope='session')
def stubmaster():
    """A kube._testing.StubMaster instance."""
    return kube._testing.StubMaster()


@pytest.fixture(scope='session')
def cluster(request, stubmaster, xprocess):
    """A kube.Cluster instance.

    Normally this will use a stubbed APIServerProxy, when --verify is
    used a real cluster is used.  In this case the argument to
    --verify is used as the context for the kubectl proxy, which will
    listen to http://localhost:8001 and will fail if it can not bind to
    this port.
    """
    cluster = kube.Cluster()
    if not request.config.getoption('verify'):
        cluster.proxy = kube._testing.StubAPIServerProxy(master=stubmaster)
        pid = None
    else:
        def prepare(cwd):    # pylint: disable=unused-argument
            return 'Starting to serve', [
                'kubectl',
                '--context', request.config.getoption('verify'),
                'proxy',
            ],
        pid, _ = xprocess.ensure('kubectl-proxy', prepare)
    def fin():
        cluster.close()
        if pid:
            os.kill(pid, signal.SIGTERM)
    request.addfinalizer(fin)
    return cluster
