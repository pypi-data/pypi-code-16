import click

from globus_cli.parsing import CaseInsensitiveChoice, common_options
from globus_cli.helpers import outformat_is_json

from globus_cli.services.auth import maybe_lookup_identity_id

from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, endpoint_list_to_text, get_client)


@click.command('search', help='Search for Globus Endpoints')
@common_options
@click.option('--filter-scope', default='all', show_default=True,
              type=CaseInsensitiveChoice(
                  ('all', 'administered-by-me', 'my-endpoints',
                   'my-gcp-endpoints', 'recently-used', 'in-use',
                   'shared-by-me', 'shared-with-me')),
              help='The set of endpoints to search over.')
@click.option('--filter-owner-id',
              help=('Filter search results to endpoints owned by a specific '
                    'identity. Can be the Identity ID, or the Identity '
                    'Username, as in "go@globusid.org"'))
@click.argument('filter_fulltext', required=False)
def endpoint_search(filter_fulltext, filter_owner_id, filter_scope):
    """
    Executor for `globus transfer endpoint-search`
    """
    client = get_client()

    owner_id = filter_owner_id
    if owner_id:
        owner_id = maybe_lookup_identity_id(owner_id)

    search_iterator = client.endpoint_search(
        filter_fulltext=filter_fulltext, filter_scope=filter_scope,
        filter_owner_id=owner_id)

    if outformat_is_json():
        print_json_from_iterator(search_iterator)
    else:
        endpoint_list_to_text(search_iterator)
