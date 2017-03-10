import params
from api import API


def describe_networks(network_ids=None,
                      status=None,
                      search_word=None,
                      limit=None,
                      offset=None,
                      reverse=None,
                      verbose=None):

        payload = {}
        payload = params.filter_ids(payload, 'networkIds', network_ids)
        payload = params.filter_status(payload, status)
        payload = params.filter_search_word(payload, search_word)
        payload = params.filter_limit(payload, limit)
        payload = params.filter_offset(payload, offset)
        payload = params.filter_reverse(payload, reverse)
        payload = params.filter_verbose(payload, verbose)

        instances = API.conn.call('DescribeNetworks', payload)
        return instances
