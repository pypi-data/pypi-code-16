import click

from odoo_rpc_client import Client


@click.group()
@click.option(
    '--conn',
    required=True,
    help='connection string for odoo-rpc-client.\n'
         'example: "xml-rpc://user:password@localhost:8069/db"')
@click.pass_context
def main(ctx, conn):
    """ CLI for odoo-rpc-client.
        Manage your Odoo instances via command line
    """
    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj['client'] = Client.from_url(conn)
