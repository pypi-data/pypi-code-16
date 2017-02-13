"""Endpoint path module.

Allow to build relative REST API endpoint path.
"""
from six.moves.urllib.parse import urlencode  # pylint: disable=import-error


def authorization():
    """Provide endpoint to user authorization endpoint.

    Along with access information PubNub service provide partial
    information about account.
    :rtype:  str
    :return: Path to user authorization endpoint.
    """
    return '/me'


def applications(identifier):
    """Provide endpoint to get list of registered applications.

    :type identifier:  int
    :param identifier: Reference on unique identifier of authorized user
                       for which applications should be retrieved.

    :rtype:  str
    :return: Target REST API endpoint which is relative to base address.
    """
    return '{0}?{1}'.format('/apps', urlencode(dict(owner_id=identifier)))


def block(keyset_id, block_id=None):
    """Provide endpoint to get block information.

    Endpoint allow to retrieve information about specific block or all
    blocks registered for keyset (if 'block_id' is 'None').
    :type keyset_id:  int
    :param keyset_id: Reference on unique identifier of application's
                      keyset for which list of blocks should be retrieved.
    :type block_id:   int | None
    :param block_id:  Reference on unique identifier of block for which
                      information should be retrieved.

    :rtype:  str
    :return: Target REST API endpoint which is relative to base address.
    """
    endpoint = '/v1/blocks/key/{0}/block'.format(keyset_id)
    if block_id:
        endpoint = '{0}/{1}'.format(endpoint, block_id)

    return endpoint


def block_state(keyset_id, block_id, state):
    """Provide endpoint which will allow change current block operation
    mode.

    Endpoint allow to retrieve information about specific block or all
    blocks registered for keyset (if 'block_id' is 'None').
    :type keyset_id:  int
    :param keyset_id: Reference on unique identifier of application's
                      keyset for which block state should be changed.
    :type block_id:   int | None
    :param block_id:  Reference on unique identifier of block for which
                      operation state should be changed.
    :type state:      str
    :param state:     Reference to one of possible block operation
                      states: start, stop.

    :rtype:  str
    :return: Target REST API endpoint which is relative to base address.
    """
    block_endpoint = block(keyset_id=keyset_id, block_id=block_id)

    return '{0}/{1}'.format(block_endpoint, state)


def event_handler(keyset_id, handler_id=None):
    """Provide endpoint which allow block's event handlers manipulation.

    :type keyset_id:   int
    :param keyset_id:  Reference on unique identifier of application's
                       keyset for which event handler access required.
    :type handler_id:  int | None
    :param handler_id: Reference on unique identifier of block's event
                       handler.

    :rtype:  str
    :return: Target REST API endpoint which is relative to base address.
    """
    endpoint = '/v1/blocks/key/{0}/event_handler'.format(keyset_id)
    if handler_id:
        endpoint = '{0}/{1}'.format(endpoint, handler_id)

    return endpoint
