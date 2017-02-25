import uuid
import json

from globus_sdk import TransferClient, RefreshTokenAuthorizer

from globus_cli import version
from globus_cli.config import (
    get_transfer_tokens, internal_auth_client, set_transfer_access_token)
from globus_cli.safeio import safeprint
from globus_cli.helpers import print_table


def _update_access_tokens(token_response):
    tokens = token_response.by_resource_server['transfer.api.globus.org']
    set_transfer_access_token(tokens['access_token'],
                              tokens['expires_at_seconds'])


def get_client():
    tokens = get_transfer_tokens()
    authorizer = None

    # if there's a refresh token, use it to build the authorizer
    if tokens['refresh_token'] is not None:
        authorizer = RefreshTokenAuthorizer(
            tokens['refresh_token'], internal_auth_client(),
            tokens['access_token'], tokens['access_token_expires'],
            on_refresh=_update_access_tokens)

    return TransferClient(authorizer=authorizer, app_name=version.app_name)


def display_name_or_cname(ep_doc):
    return ep_doc['display_name'] or ep_doc['canonical_name']


def print_json_from_iterator(iterator):
    json_output_dict = {'DATA': []}
    for item in iterator:
        dat = item
        try:
            dat = item.data
        except AttributeError:
            pass
        json_output_dict['DATA'].append(dat)
    safeprint(json.dumps(json_output_dict, indent=2))


def endpoint_list_to_text(iterator):
    print_table(iterator, [('ID', 'id'), ('Owner', 'owner_string'),
                           ('Display Name', display_name_or_cname)])


def assemble_generic_doc(datatype, **kwargs):
    doc = {'DATA_TYPE': datatype}
    for key, val in kwargs.items():
        if isinstance(val, uuid.UUID):
            val = str(val)
        if val is not None:
            doc[key] = val
    return doc


def autoactivate(client, endpoint_id, if_expires_in=None):
    kwargs = {}
    if if_expires_in is not None:
        kwargs['if_expires_in'] = if_expires_in

    return client.endpoint_autoactivate(endpoint_id, **kwargs)
