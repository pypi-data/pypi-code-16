from __future__ import print_function, absolute_import

import getopt
import json
import os
import shutil
import sys
import tempfile

from ipykernel.eventloops import register_integration
from ipykernel.kernelapp import IPKernelApp
from pyq import q, K, kerr

import traceback
MIN_PORT = 1024
MAX_PORT = 65535
app = None


def kernel_spec():
    executable = os.getenv('QBIN')
    spec = {
        "argv": [executable, "ker.q", str(MIN_PORT), str(MAX_PORT), "{connection_file}", ],
        "display_name": "PyQ+ %d" % sys.version_info[0],
        "language": "python"
    }
    env = {}
    for name in ['QHOME', 'QLIC', 'CPUS']:
        value = os.getenv(name)
        if value is not None:
            env[name] = value
    if env:
        spec['env'] = env
    return spec


def install_kernel_spec(name, user, prefix):
    from jupyter_client.kernelspec import KernelSpecManager
    from .icons import make_logo
    ksm = KernelSpecManager()
    spec = kernel_spec()
    td = tempfile.mkdtemp()
    try:
        os.chmod(td, 0o755)
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(spec, f, sort_keys=True, indent=4)
        make_logo(td)
        print('Installing "%(display_name)s" kernel spec.' % spec)
        ksm.install_kernel_spec(td, name, user=user, replace=True, prefix=prefix)
    finally:
        shutil.rmtree(td)


def i1():
    try:
        app.kernel.do_one_iteration()
    except Exception:
        traceback.print_exc(None, sys.__stderr__)
        traceback.print_tb(sys.exc_info()[-1], None, sys.__stderr__)

    return K(None)


@register_integration('q')
def loop_q(_):
    q.i1 = i1
    q('.z.ts:{i1()}')
    app.kernel._poll_interval = 0.3
    poll_interval = int(0.7 * 1000 * app.kernel._poll_interval)
    q('\\t %s' % poll_interval)


def is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False  # assume not an admin on non-Unix platforms


def main(argv):
    name = 'pyq_%d' % sys.version_info[0]
    prefix = None
    user = not is_root()

    opts, _ = getopt.getopt(argv, '', ['user', 'prefix=', 'min-port=', 'max-port='])
    for k, v in opts:
        if k == '--user':
            user = True
        elif k == '--prefix':
            prefix = v
            user = False
        elif k == '--name':
            name = v
        elif k == '--min-port':
            global MIN_PORT
            MIN_PORT = int(v)
        elif k == '--max-port':
            global MAX_PORT
            MAX_PORT = int(v)

    install_kernel_spec(name, user, prefix)


def start():
    global app
    app = IPKernelApp.instance()
    args = [str(a) for a in q('.z.x')]
    app.initialize(['-f', args[-1]])
    app.shell.enable_gui('q')
    app.shell.extension_manager.load_extension('pyq.magic')
    app.kernel.start()
    loop_q(app.kernel)
    min_port, max_port = map(int, args[:2])
    for port in range(min_port, max_port + 1):
        try:
            q('\\p %d' % port)
        except kerr:
            pass
        else:
            break

if __name__ == '__main__':

    if len(sys.argv) < 2 or sys.argv[1] != 'install':
        print("""\
Usage: pyq -mpyq.kernel install [options]

    Options:

       --user - user install;
       --prefix=<dir> - system install in dir;
       --min-port=<port> - minimal port to try for the kdb+ server;
       --max-port=<port> - largest port to try for the kdb+ server.
""")
    else:
        main(argv=sys.argv[2:])
