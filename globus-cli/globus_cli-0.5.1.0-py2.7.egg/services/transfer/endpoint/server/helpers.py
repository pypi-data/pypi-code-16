import click

from globus_cli.helpers import CaseInsensitiveChoice


def add_and_update_opts(add=False):
    def inner_decorator(f):
        f = click.option('--hostname', required=add,
                         help='Server Hostname.')(f)

        default_scheme = 'gsiftp' if add else None
        f = click.option(
            '--scheme', help='Scheme for the Server.',
            type=CaseInsensitiveChoice(('gsiftp', 'ftp')),
            default=default_scheme, show_default=add)(f)

        default_port = 2811 if add else None
        f = click.option(
            '--port', help='Port for Globus control channel connections.',
            type=int, default=default_port, show_default=add)(f)

        f = click.option(
            '--subject',
            help=('Subject of the X509 Certificate of the server. When '
                  'unspecified, the CN must match the server hostname.'))(f)

        return f
    return inner_decorator


def server_id_option(f):
    f = click.option('--server-id', required=True, help='ID of the Server')(f)
    return f
