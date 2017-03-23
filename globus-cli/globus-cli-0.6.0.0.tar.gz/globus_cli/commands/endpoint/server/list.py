import json
from textwrap import dedent
import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import (colon_formatted_print, print_table,
                                outformat_is_json)
from globus_cli.services.transfer import (display_name_or_cname,
                                          get_client, print_json_from_iterator)


@click.command('list', help='List all servers belonging to an Endpoint')
@common_options
@endpoint_id_arg
def server_list(endpoint_id):
    """
    Executor for `globus endpoint server list`
    """
    client = get_client()

    endpoint = client.get_endpoint(endpoint_id)

    if endpoint['host_endpoint_id']:  # not GCS -- this is a share endpoint
        raise click.UsageError(dedent("""\
            {id} ({0}) is a share and does not have servers.

            To see details of the share, use
                globus endpoint show {id}

            To list the servers on the share's host endpoint, use
                globus endpoint server list {host_endpoint_id}
        """).format(display_name_or_cname(endpoint), **endpoint.data))

    if endpoint['s3_url']:  # not GCS -- this is an S3 endpoint
        if outformat_is_json():
            safeprint(json.dumps({'s3_url': endpoint['s3_url']}, indent=2))
        else:
            colon_formatted_print(endpoint, [("S3 URL", 's3_url')])
        return

    # regular GCS host endpoint; use Transfer's server list API
    server_iterator = client.endpoint_server_list(endpoint_id)

    if outformat_is_json():
        print_json_from_iterator(server_iterator)
    else:
        print_table(server_iterator, [
            ('ID', 'id'),
            ('URI', lambda s: s['uri'] or "none (Globus Connect Personal)"),
        ])
