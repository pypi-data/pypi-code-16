import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import (
    common_options, endpoint_id_option, endpoint_create_and_update_opts)
from globus_cli.helpers import outformat_is_json, print_json_response
from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)


@click.command('update', help='Update attributes of a Share')
@common_options
@endpoint_create_and_update_opts(create=False, shared_ep=True)
@endpoint_id_option(help='ID of the Share')
def share_update(endpoint_id, display_name, description, organization,
                 contact_email, contact_info, info_link, public):
    """
    Executor for `globus transfer share update`
    """
    client = get_client()

    ep_doc = assemble_generic_doc(
        'endpoint',
        display_name=display_name, description=description,
        organization=organization, contact_email=contact_email,
        contact_info=contact_info, info_link=info_link, public=public)

    res = client.update_endpoint(endpoint_id, ep_doc)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
