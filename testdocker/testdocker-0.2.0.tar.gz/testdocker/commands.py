"""
testdocker.commands
~~~~~~~~~~~~~~

Commands classes for docker testing.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

from . import util


class CommandBase:
    def __str__(self):
        return self.cmd

class CurlCommand(CommandBase):
    defaults = dict(
        options=dict(
            silent=True,
            fail=True
        )
    )
    def __init__(self, url, method='GET', headers=None, data=None,
                 options=None, **kwargs):
        headers = headers or {}
        data = data or {}
        options = util.set_defaults(options or {}, self.defaults['options'])

        cmd = ['curl']
        cmd.append(self.build_args(options))
        if method != 'GET':
            cmd.append('-X %s' % method)
        if headers:
            for header in headers:
                cmd.append("-H '%s: %s'" % header)
        if data:
            if isinstance(data, dict):
                data = json.dumps(data)
            cmd.append("--data '%s'" % data)
        cmd.append(url)
        self.cmd = ' '.join(cmd)

    @staticmethod
    def build_args(options):
        args = []
        if options.get('silent'):
            args.append('-s')
        if options.get('fail'):
            args.append('-f')
        return ' '.join(args)


class NetCatCommand(CommandBase):
    def __init__(self, host, port, udp=False):
        cmd = ['nc', '-z', host, str(port)]
        if udp:
            cmd.append('-u')
        self.cmd = ' '.join(cmd)


class CatCommand(CommandBase):
    def __init__(self, path):
        cmd = ['cat', path]
        self.cmd = ' '.join(cmd)
