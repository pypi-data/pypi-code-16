import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import (
    outformat_is_json, print_json_response, colon_formatted_print)

from globus_cli.services.transfer import get_client


@click.command('show', help='Display a detailed Endpoint definition')
@common_options
@endpoint_id_arg
def endpoint_show(endpoint_id):
    """
    Executor for `globus endpoint show`
    """
    client = get_client()

    res = client.get_endpoint(endpoint_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        fields = (('Display Name', 'display_name'), ('ID', 'id'),
                  ('Owner', 'owner_string'), ('Activated', 'activated'),
                  ('Shareable', 'shareable'),
                  ('Department', 'department'), ('Keywords', 'keywords'))
        colon_formatted_print(res, fields)
