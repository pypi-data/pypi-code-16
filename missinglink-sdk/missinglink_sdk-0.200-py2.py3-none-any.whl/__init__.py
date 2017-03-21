# coding=utf-8
import os
import sys
import logging
import ssl
from subprocess import Popen, PIPE
import os.path

from .sdk_version import get_version, get_keywords

loaded = False
__version__ = get_version()
keywords = get_keywords() or []
is_python2 = sys.version_info[0] == 2


def get_pip_server():
    pypi_server_hostname = 'testpypi' if 'test' in keywords else 'pypi'

    return 'https://{hostname}.python.org/pypi'.format(hostname=pypi_server_hostname)


def get_latest_pip_version():
    try:
        if is_python2:
            from xmlrpclib import ServerProxy, SafeTransport
        else:
            from xmlrpc.client import ServerProxy, SafeTransport

        if sys.version_info >= (2, 7, 9):
            context = None
            if hasattr(ssl, '_create_unverified_context'):
                # noinspection PyProtectedMember
                context = ssl._create_unverified_context()

            transport = SafeTransport(use_datetime=True, context=context)
        else:
            transport = SafeTransport(use_datetime=True)

        pypi_server = get_pip_server()

        latest_version = ServerProxy(pypi_server, transport=transport).package_releases('missinglink-kernel')[0]

        return latest_version
    except Exception as e:
        logging.exception('could not check for new missinglink-sdk version:\n%s', str(e))
        return None


def update_sdk(latest_version, user_path=False):
    python_bin_path = sys.executable
    pip_bin_path = os.path.join(os.path.dirname(python_bin_path), 'pip')
    if not os.path.exists(pip_bin_path):
        logging.warning("pip not found, can't self update missinglink sdk")
        return False

    if user_path:
        args = (pip_bin_path, 'install', '--upgrade', '--user', '-i', get_pip_server(), 'missinglink-sdk==%s' % latest_version)
    else:
        args = (pip_bin_path, 'install', '--upgrade', '-i', get_pip_server(), 'missinglink-sdk==%s' % latest_version)

    try:
        p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        output, err = p.communicate()
    except Exception:
        logging.exception("%s failed", " ".join(args))
        return False

    rc = p.returncode

    if rc == 0:
        logging.info('MissingLink SDK updated to latest version (%s)', latest_version)
    else:
        logging.error('MissingLink SDK failed to upgrade to latest version (%s)', latest_version)
        logging.error("failed to run %s (%s)\n%s\n%s", " ".join(args), rc, err, output)

    return rc == 0


# noinspection PyCompatibility,PyUnresolvedReferences,PyBroadException
def self_update():
    global __version__

    if __version__ is None:
        __version__ = 'Please install this project with setup.py'
        return

    latest_version = get_latest_pip_version()

    if latest_version is None:
        return

    if str(__version__) == latest_version:
        return

    running_under_virtualenv = hasattr(sys, 'real_prefix')

    if running_under_virtualenv:
        update_sdk(latest_version)
    else:
        logging.info('updating missing link sdk to version %s in user path', latest_version)
        update_sdk(latest_version, user_path=True)


def do_import():
    import missinglink_kernel
    global __version__
    __version__ = missinglink_kernel.get_version()

    from missinglink_kernel import KerasCallback, TensorFlowCallback, PyTorchCallback, PyCaffeCallback

    return KerasCallback, TensorFlowCallback, PyTorchCallback, PyCaffeCallback

self_update()
KerasCallback, TensorFlowCallback, PyTorchCallback, PyCaffeCallback = do_import()


def debug_missinglink_on():
    logging.basicConfig()
    missinglink_log = logging.getLogger('missinglink')
    missinglink_log.setLevel(logging.DEBUG)
    missinglink_log.propagate = False
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    missinglink_log.addHandler(ch)


__all__ = ['KerasCallback', 'TensorFlowCallback', 'PyTorchCallback', 'PyCaffeCallback', 'debug_missinglink_on']
