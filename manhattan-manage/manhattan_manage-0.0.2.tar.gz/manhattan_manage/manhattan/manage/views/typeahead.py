"""
Generic typeahead document chain.

The generic typeahead view is designed to return *all* relevant results for a
user query and leaves the final filtering and sorting of the results to the
client-side caller.
"""

import re

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan import formatters
from mongoframes import ASC, DESC, InvalidPage, Or, Paginator, Q

from . import factories
from .utils import json_fail, json_success

__all__ = ['typeahead_chains']


# Define the chains
typeahead_chains = ChainMgr()

# GET
typeahead_chains['get'] = Chain([
    'authenticate',
    'search',
    'select',
    'render_json'
])


# Define the links
typeahead_chains.set_link(factories.authenticate())

@typeahead_chains.link
def search(state):
    """
    Build a database query based on the `q` parameter within the request to
    filter the typeahead results.

    This link adds the `query` key to the state containing the database query.
    """
    state.query = None

    # If the query isn't long enough to query the database then return a failed
    # response.
    q = flask.request.args.get('q', '').strip()
    if len(q) < state.manage_config.typeahead_match_len:
        return json_fail(
            'The query string is too short, it should be at least {0} '
            'characters long'.format(state.manage_config.typeahead_match_len)
            )

    # Replace accented characters in the string with closest matching
    # equivalent non-accented characters.
    q = formatters.text.remove_accents(q)

    # Shorten the query string to the match length
    q = q[:state.manage_config.typeahead_match_len]

    # Make the query safe for regular expressions
    q = re.escape(q)

    # Build the query to search
    typeahead_field = state.manage_config.typeahead_field

    assert typeahead_field, 'No typeahead field defined'

    if state.manage_config.typeahead_match_type == 'contains':
        state.query = Q[typeahead_field] == re.compile(q)
    elif state.manage_config.typeahead_match_type == 'startswith':
        state.query = Q[typeahead_field] == re.compile(r'^' + q)

    assert state.query, "'{0}' is not a valid typeahead match type"

@typeahead_chains.link
def select(state):
    """
    Select the documents for the typeahead.

    This link adds the `{state.manage_config.var_name_plural}` key to the state
    containing the selected database documents.
    """

    # Select the documents
    documents = state.manage_config.frame_cls.many(
        state.query,
        projection=state.manage_config.typeahead_projection
        )

    state[state.manage_config.var_name_plural] = documents

@typeahead_chains.link
def render_json(state):
    """
    Convert the selected documents to a JSON result for the client-side
    typeahead.
    """

    # Convert the matching documents into a list of items for the typeahead
    items = []
    for document in state[state.manage_config.var_name_plural]:
        item = {}

        # Id
        if state.manage_config.typeahead_id_attr:
            item['id'] = getattr(
                document,
                state.manage_config.typeahead_id_attr
                )
        else:
            item['id'] = str(document._id)

        # Value
        item['value'] = getattr(
            document,
            state.manage_config.typeahead_field
            )

        # Label
        if state.manage_config.typeahead_label_attr:
            item['label'] = getattr(
                document,
                state.manage_config.typeahead_label_attr
                )
        else:
            item['label'] = str(document)

        items.append(item)

    return json_success({'items': items})