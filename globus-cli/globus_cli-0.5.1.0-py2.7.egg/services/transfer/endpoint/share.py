import click

from globus_cli.parsing import (
    common_options, endpoint_create_and_update_params, ENDPOINT_PLUS_REQPATH)
from globus_cli.helpers import print_json_response
from globus_cli.services.transfer.activation import autoactivate
from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)


@click.command('share', help='Create a new Share, hosted on an Endpoint')
@common_options
@click.argument('endpoint_plus_path', metavar='HOST_ENDPOINT_ID:HOST_PATH',
                type=ENDPOINT_PLUS_REQPATH)
@endpoint_create_and_update_params(create=True, shared_ep=True)
def endpoint_create_share(endpoint_plus_path, display_name, description,
                          organization, contact_email, contact_info,
                          info_link):
    """
    Executor for `globus transfer share create`
    """
    endpoint_id, host_path = endpoint_plus_path

    ep_doc = assemble_generic_doc(
        'shared_endpoint',
        host_endpoint=endpoint_id, host_path=host_path,
        display_name=display_name, description=description,
        organization=organization, contact_email=contact_email,
        contact_info=contact_info, info_link=info_link, public=True)

    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)
    res = client.create_shared_endpoint(ep_doc)
    print_json_response(res)
