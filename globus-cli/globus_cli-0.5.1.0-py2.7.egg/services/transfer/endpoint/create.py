import click

from globus_cli.parsing import (
    common_options, endpoint_create_and_update_params)
from globus_cli.helpers import print_json_response

from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)


@click.command('create', help='Create a new Endpoint')
@common_options
@endpoint_create_and_update_params(create=True)
@click.option('--globus-connect-server', 'endpoint_type', flag_value='server',
              help='This endpoint is a Globus Connect Server endpoint')
@click.option('--globus-connect-personal', 'endpoint_type',
              flag_value='personal', default=True, show_default=True,
              help='This endpoint is a Globus Connect Personal endpoint')
def endpoint_create(endpoint_type, display_name, description, organization,
                    contact_email, contact_info, info_link, public,
                    default_directory, force_encryption, oauth_server,
                    myproxy_server, myproxy_dn):
    """
    Executor for `globus transfer endpoint create`
    """
    ep_doc = assemble_generic_doc(
        'endpoint',
        # omit this key if not personal, but include as True if personal
        is_globus_connect=(endpoint_type == 'personal' or None),
        display_name=display_name, description=description,
        organization=organization, contact_email=contact_email,
        contact_info=contact_info, info_link=info_link,
        force_encryption=force_encryption, public=public,
        default_directory=default_directory,
        myproxy_server=myproxy_server, myproxy_dn=myproxy_dn,
        oauth_server=oauth_server)

    client = get_client()
    res = client.create_endpoint(ep_doc)
    print_json_response(res)
