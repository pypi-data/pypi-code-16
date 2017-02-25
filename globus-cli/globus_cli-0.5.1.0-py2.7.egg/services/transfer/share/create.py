import click

from globus_cli.parsing import common_options, endpoint_create_and_update_opts
from globus_cli.helpers import print_json_response
from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)


@click.command('create', help='Create a new Share, hosted on an Endpoint')
@common_options
@endpoint_create_and_update_opts(create=True, shared_ep=True)
@click.option('--host-endpoint-id', required=True,
              help='ID of the endpoint on which this Share is hosted')
def share_create(host_endpoint_id, display_name, description, organization,
                 contact_email, contact_info, info_link, public):
    """
    Executor for `globus transfer share create`
    """
    ep_doc = assemble_generic_doc(
        'shared_endpoint', host_endpoint_id=host_endpoint_id,
        display_name=display_name, description=description,
        organization=organization, contact_email=contact_email,
        contact_info=contact_info, info_link=info_link, public=public)

    client = get_client()
    res = client.create_endpoint(ep_doc)
    print_json_response(res)
