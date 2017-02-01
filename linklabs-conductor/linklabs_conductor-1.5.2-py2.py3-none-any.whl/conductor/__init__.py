"""
This module wraps the Conductor API.
"""

import logging
from time import sleep
from datetime import datetime, timedelta
from collections import namedtuple
from getpass import getpass
from operator import itemgetter
from copy import deepcopy
import json
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
import sys
import warnings

import requests
import dateutil.parser

LOG = logging.getLogger(__name__)
CLIENT_EDGE_URL = 'https://clientedge-conductor.link-labs.com/clientEdge'
NETWORK_ASSET_URL = 'https://networkasset-conductor.link-labs.com/networkAsset'
ACCESS_URL = 'https://access-conductor.link-labs.com/access'
CLIENT_EDGE_POLL_PERIOD_S = 1.0
ALLOWED_PORT_RANGE = range(0, 128)


UplinkMessage = namedtuple('UplinkMessage', ['module', 'gateway', 'payload_hex', 'port',
                                             'receive_time', 'uuid', 'network_token',
                                             'packet_data'])


PacketSignalData = namedtuple('PacketSignalData', ['spreading_factor', 'snr', 'rssi', 'frequency'])


class ConductorSubject(object):
    """
    Base class for subclasses that are Conductor subjects.

    All subjects need a subject name (unique to the class),
    subject ID (unique to the object), and an authenticated session.
    """
    subject_name = None

    def __init__(self, session, subject_id, _data=None):
        self.session = session
        self.subject_id = subject_id
        self._data = _data

    def __str__(self):
        return str(self.subject_id)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.subject_id == other.subject_id
        return NotImplemented

    def __neq__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash((self.subject_name, self.subject_id))

    def http_get(self, *args, **kwargs):
        return _handle_conductor_response(self.session.get(*args, **kwargs))

    def http_post(self, *args, **kwargs):
        return _handle_conductor_response(self.session.post(*args, **kwargs))


class UplinkSubjectBase(ConductorSubject):
    """
    Base class for things that can be queried against for uplink payloads.
    This should not be used directly.
    """

    def _yield_messages_time_range(self, start, stop=None):
        """
        Gets messages within a time range. Yields the messages one
        at a time. Messages may be ordered randomly.
        """
        stop = stop or datetime.utcnow()
        url = CLIENT_EDGE_URL + '/data/uplinkPayload/{}/{}/events/{}/{}'.format(
            self.subject_name, self.subject_id, format_time(stop), format_time(start)
        )
        next_page_id = None
        while True:
            resp_data = self.http_get(url, params={'pageId': next_page_id})
            for msg in resp_data['results']:
                yield _result_to_uplink_message(msg)

            next_page_id = resp_data.get('nextPageId')
            if not next_page_id:
                break
            LOG.debug("Getting next page for same request")

    def get_messages_time_range(self, start, stop=None):
        """
        Retrieves all messages within a start and stop time.

        The `start` and `stop` arguments must be `datetime.datetime` objects.
        If `stop` is `None`, then the current time will be used.

        Returns a list of `UplinkMessage` objects sorted by time.
        """
        messages = list(self._yield_messages_time_range(start, stop))
        messages = sorted(messages, key=lambda m: m.receive_time)
        return messages

    def get_recent_messages(self, mins_back):
        """ Gets the messages received in the last `mins_back` minutes. """
        now = datetime.utcnow()
        return self.get_messages_time_range(now - timedelta(minutes=mins_back))

    def subscribe(self, on_receive, on_close=None):
        """
        Sets up a subscription. The `on_receive` callback will be called
        with an `UplinkMessage` argument for every received message.
        The `on_close` callback, if supplied, will be called when the
        subscription closes.

        Returns a Subscription object. Call the `close` method on
        the subscription object when done.
        """
        from ws4py.client.threadedclient import WebSocketClient
        class Subscription(WebSocketClient):
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.close()

            def received_message(self, message):
                """ Method called on every received message. """
                LOG.debug("Received subscription message: %s", message)
                on_receive(_result_to_uplink_message(json.loads(str(message))))

            def closed(self, code, reason=None):
                LOG.info("Closing subscription: %s, %s", code, reason)
                if on_close:
                    on_close()

        # Get the websocket URL
        url = CLIENT_EDGE_URL + '/data/uplinkPayload/{}/{}/subscriptions'.format(
            self.subject_name, self.subject_id
        )
        data = {
            'channelRequest': {'type': 'Websocket'},
            'subscriptionProperties': {'filterProperties': []}
        }
        resp = self.session.post(url, json=data)
        resp.raise_for_status()
        ws_url = resp.json()['websocketUrl']['href']

        sub = Subscription(ws_url, headers=resp.request.headers.items(), heartbeat_freq=2.0)
        sub.connect()

        return sub


class ChunkedUplinkSubject(UplinkSubjectBase):
    """
    A class (mix-in) for breaking large requests into chunks to reduce each request's size.

    DEPRECATED: This functionality is deprecated as it's now handled in `get_messages_time_range`.
    """

    def get_messages_time_range_chunked(self, start, stop=None, num_chunks=1):
        """
        The same as `get_messages_time_range`, but break the request to Conductor into
        `num_chunks` different requests.

        This method is deprecated.
        """
        warnings.warn("`get_messages_time_range_chunked` is deprecated. "
                      "Use `get_messages_time_range` instead")
        return self.get_messages_time_range(start, stop)


class UplinkSubscriptionIterator(UplinkSubjectBase):
    """
    A mix-in providing a helper method for returning a synchronous
    subscription generator.
    """
    def subscribe_iter(self):
        """
        Sets up a subscription, but returns a generator that yields
        `UplinkMessage` object and returns when the subscription
        is closed.
        """
        queue = Queue()

        def callback(message):
            """ Puts the message in the thread-safe queue to be received synchronously. """
            queue.put(message)

        with self.subscribe(callback) as sub:
            while True:
                try:
                    message = queue.get(timeout=0.2)
                    yield message
                except Empty:
                    if sub.client_terminated or sub.server_terminated:
                        return


class UplinkSubject(ChunkedUplinkSubject, UplinkSubscriptionIterator, UplinkSubjectBase):
    """ A class combining the mixins for all uplink subjects. """
    pass


class DownlinkSubject(ConductorSubject):
    """ A class for sending downlink messages. """
    def _send_message_with_body(self, body, payload, acked=True,
                                time_to_live_s=60.0, port=0, priority=10):
        if port not in ALLOWED_PORT_RANGE:
            raise ValueError("Port must be within [0, 127]")

        url = CLIENT_EDGE_URL + '/issueCommand'

        # We're only looking for one link to respond
        ack_ratio = sys.float_info.epsilon if acked else 0

        body['commandProperties'] = {
            "payloadHex": hexlify(payload),
            "commReqs": {
                "requiredAckRatio": ack_ratio,
                "requiredSuccessfulAckRatio": ack_ratio,
                "priority": int(priority),
                "ttlMSecs": int(time_to_live_s * 1000),
                "portNumber": port,
            }
        }

        data = self.http_post(url, json=body)
        issuance_id = data['issuanceId']
        return DownlinkMessage(self.session, issuance_id, _data=data)

    def query_downlink(self, start, stop=None):
        """ Queries Conductor for all downlink sent to this subject. """
        stop = stop or datetime.utcnow()
        url = CLIENT_EDGE_URL + '/commands/{}/{}/{}/{}'.format(
            self.subject_name, self.subject_id, format_time(stop), format_time(start))
        data = self.http_get(url)
        return [DownlinkMessage(self.session, result['issuanceId'], _data=result)
                for result in data]


class ConductorAccount(UplinkSubject):
    """
    This class provides methods for interacting with Conductor for a particular account.

    This is the starting point for everything else in this module. Initialize with your
    username and password. If the password is omitted the initializer will prompt for one.
    Optionally provide the account name that you're trying to access (if you don't provide
    the account, the constructor will try to figure out which account is linked to your username).
    """

    subject_name = 'accountId'

    def __init__(self, username, password=None, account_name=None):
        password = password or getpass('Conductor password for {}:'.format(username))
        self.session = requests.Session()
        self.session.auth = requests.auth.HTTPBasicAuth(username, password)

        if account_name:
            # Find account ID for the account name, if given
            account = self.http_get('{}/accountName/{}'.format(ACCESS_URL, account_name))
        else:
            # Look up all the accounts associated with this user, and use the first one.
            accounts = self._get_accounts()
            LOG.debug("Got accounts: %s", accounts)
            if len(accounts) == 0:
                raise RuntimeError("No account associated with username")
            elif len(accounts) > 1:
                LOG.warning("More than one account associated with username")
            account = accounts[0]

        self.account_id = account['id']
        self.account_name = account['name']

        super(ConductorAccount, self).__init__(self.session, self.account_id, _data=account)

    def __str__(self):
        return self.account_name

    def _get_accounts(self):
        """ Gets the accounts associated with this username. Returns a list of dictionaries. """
        url = ''.join([ACCESS_URL, '/accounts'])
        return self.http_get(url, params={'username': self.session.auth.username})

    def _get_registered_asset(self, subject_name, subject_id):
        """ Base function for getting a registered asset from the Network Asset API. """
        url = ''.join([NETWORK_ASSET_URL, '/{}/{}'.format(subject_name, subject_id)])
        return self.http_get(url)

    def _get_registered_assets(self, asset_name):
        """ Base function for getting list of registered assets from the Network Asset API. """
        url = ''.join([NETWORK_ASSET_URL, '/', asset_name])
        params = {'accountId': self.account_id, 'lifecycle': 'registered'}
        return self.http_get(url, params=params)

    def get_gateways(self):
        """ Returns a list of `Gateway` objects that have been registered to this account. """
        return [Gateway(self.session, x['nodeAddress'], x.get('registrationToken'), _data=x)
                for x in self._get_registered_assets('gateways')]

    def get_gateway(self, gateway_addr):
        """ Opens a gateway by address. Returns a `Gateway` object. """
        asset = self._get_registered_asset('gateway', gateway_addr)
        return Gateway(self.session, gateway_addr, asset.get('registrationToken'), _data=asset)

    def get_modules(self):
        """ Returns a list of `Module` objects that have been registered to this account. """
        return [Module(self.session, x['nodeAddress'], _data=x)
                for x in self._get_registered_assets('modules')]

    def get_module(self, module_addr):
        """ Opens a module by address. Returns a 'Module' object. """
        asset = self._get_registered_asset('module', module_addr)
        return Module(self.session, module_addr, _data=asset)

    def get_application_tokens(self):
        """ Returns a list of application tokens that have been registered to this account. """
        return [AppToken(self.session, x['hash'], _data=x)
                for x in self._get_registered_assets('applicationTokens')]

    def get_application_token(self, app_token_hash):
        """ Opens an application token object by hash. Returns an `AppToken` object. """
        asset = self._get_registered_asset('applicationToken', app_token_hash)
        return AppToken(self.session, app_token_hash, _data=asset)

    def get_network_tokens(self):
        """ Returns a list of network tokens that have been registered to this account. """
        return [NetToken(self.session, x['hash'], _data=x)
                for x in self._get_registered_assets('networkTokens')]

    def get_network_token(self, net_token_hash):
        """ Opens a network token object by hash. Returns a `NetToken` object. """
        asset = self._get_registered_asset('networkToken', net_token_hash)
        return NetToken(self.session, net_token_hash, _data=asset)


class AppToken(UplinkSubject, DownlinkSubject):
    """ Represents an application designated by an app token for an account. """
    subject_name = 'applicationToken'

    def send_message(self, payload, gateway_addr=None, acked=False,
                     time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a multicast message to all nodes registered to this app token.

        The 'acked' parameter is there to have the same function signature as other 'send_message'
        methods, but it must be False.
        """
        if acked:
            raise ValueError("Multicast messages cannot be acknowledged")

        body = {}
        if gateway_addr:
            body['commandRoutes'] = {
                'linkAddresses': [self._to_node_address() + '!101!' + gateway_addr]}
        else:
            body['commandTargets'] = {'targetAppToken': self.subject_id}

        return self._send_message_with_body(body, payload, False, time_to_live_s, port, priority)

    # We need to override query_downlink because we need to use the node address form
    def query_downlink(self, *args, **kwargs):
        """ Queries Conductor for all downlink sent to this subject. """
        temp = deepcopy(self)
        temp.subject_name = 'node'
        temp.subject_id = self._to_node_address()
        return super(AppToken, temp).query_downlink(*args, **kwargs)

    def _to_node_address(self):
        """
        Converts an app token to the node address format that Conductor understands.

        Example
        -------
        >>> app_token
        AppToken(1bcda4a2e8c1af83d330)
        >>> app_token._to_node_address()
        '$401$1bcda4a2-e8c1af83-0-00000d330'
        """
        app_token = str(self.subject_id)
        return '$401${}-{}-{}-{:0>9}'.format(app_token[:8], app_token[8:16], 0, app_token[16:])


class NetToken(UplinkSubject):
    """ Represents a network designated by a network token for an account. """
    subject_name = 'networkToken'


class Gateway(UplinkSubject, DownlinkSubject):
    """ Represents a single Symphony gateway. """
    subject_name = 'node'

    def __init__(self, session, gateway_id, network_token, _data=None):
        self.network_token = network_token
        super(Gateway, self).__init__(session, gateway_id, _data)

    def get_status(self):
        """ Returns the most recent gateway status dictionary """
        url = ''.join([CLIENT_EDGE_URL, '/data/gatewayStatus/node/',
                       self.subject_id, '/mostRecentEvents'])
        resp_data = self.http_get(url)
        return flatten_status(resp_data['results'])

    def get_statuses(self, start_time, stop_time):
        """ Returns the status messages for a particular time range. """
        url = ''.join([CLIENT_EDGE_URL, '/data/gatewayStatus/node/',
                       self.subject_id,
                       '/events/{}/{}'.format(format_time(stop_time), format_time(start_time))])
        resp_data = self.http_get(url)
        return flatten_status(resp_data['results'])

    def send_broadcast(self, payload, time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a broadcast message to all nodes listening to this gateway.

        Returns a `DownlinkMessage` object.
        """
        broadcast_mod_address = '$301$0-0-0-FFFFFFFFF'
        body = {'commandRoutes':
                {'linkAddresses': [broadcast_mod_address + '!101!' + self.subject_id]}}
        return self._send_message_with_body(body, payload, False, time_to_live_s, port, priority)


class Module(UplinkSubject, DownlinkSubject):
    """ Represents a single Module (end node). """
    subject_name = 'node'

    def send_message(self, payload, gateway_addr=None, acked=True,
                     time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a downlink message to a node. If the `gateway_addr` is specified,
        then the message will be sent through that gateway. Otherwise, Conductor
        will route the message automatically.

        `payload` should be a bytearray or bytes object.

        Returns a `DownlinkMessage` object, which can be used to poll for the message's
        status or cancel the message.
        """

        body = {}
        if gateway_addr:
            body['commandRoutes'] = {'linkAddresses': [self.subject_id + '!101!' + gateway_addr]}
        else:
            body['commandTargets'] = {'targetNodeAddresses': [self.subject_id]}

        return self._send_message_with_body(body, payload, acked, time_to_live_s, port, priority)

    def get_metadata(self):
        """ Gets the metadata for the subject """
        url = NETWORK_ASSET_URL + '/module/{}/metadata'.format(self.subject_id)
        return self.http_get(url)

    def get_routes(self):
        """ Gets the routes for the subject """
        url = CLIENT_EDGE_URL + '/module/{}/routes'.format(self.subject_id)
        return self.http_get(url)


class DownlinkMessage(ConductorSubject):
    """ This class represents a downlink message that has already been posted. """

    @property
    def issuance_id(self):
        """ The issuance ID is the subject ID from the ConductorSubject base class. """
        return self.subject_id

    def get_status(self):
        """ Gets the status of the downlink message.  """
        url = CLIENT_EDGE_URL + '/issuedCommand/{}/status'.format(self.issuance_id)
        return self.http_get(url)['status']

    def get_routes(self):
        """ Returns the routes that Conductor used for this message. """
        url = CLIENT_EDGE_URL + '/issuedCommand/{}'.format(self.issuance_id)
        resp_data = self.http_get(url)
        return [assignment['assignedLink'] for assignment in resp_data['routeAssignments']]

    def get_events(self, route=None):
        """
        Returns the events on the message and their timestamps.
        Returns a dictionary mapping routes to a list of (state, datetime) pairs.
        If `route` is specified, only the events for the specified route will be retrieved (the
        return type will be the same).

        Example
        -------
        >>> msg.get_events()
        {'$301$0-0-0-030001665!101!$101$0-0-0-db935317c': [
          ('Issued', datetime.datetime(2016, 6, 9, 21, 45, 56, 585000)),
          ('Submitting', datetime.datetime(2016, 6, 9, 21, 45, 57, 158000)),
          ('Submitted', datetime.datetime(2016, 6, 9, 21, 45, 57, 349000)),
          ('Sending', datetime.datetime(2016, 6, 9, 21, 45, 57, 403000)),
          ('Sent', datetime.datetime(2016, 6, 9, 21, 45, 57, 945000)),
          ('Expired', datetime.datetime(2016, 6, 9, 21, 47, 36, 531000))],
         '$301$0-0-0-030001665!101!$101$0-0-0-db9360dc0': [
          ('Issued', datetime.datetime(2016, 6, 9, 21, 45, 56, 585000)),
          ('Expired', datetime.datetime(2016, 6, 9, 21, 47, 36, 531000))]}
        """
        routes = [route] if route is not None else self.get_routes()
        route_urls = [CLIENT_EDGE_URL + '/issuedCommand/{}/statusDetail/{}'.format(
            self.issuance_id, rte) for rte in routes]

        results = {}
        for url in route_urls:
            resp_data = self.http_get(url)
            route = resp_data['routeAssignment']['assignedLink']
            events = [(event['state'], parse_time(event['stateTime']))
                      for event in resp_data['downlinkEvents']]
            events.sort(key=itemgetter(1))
            results[route] = events

        return results

    def cancel(self):
        """ Cancels a pending downlink message. """
        LOG.debug("Deleting downlink message %s", self.issuance_id)
        url = CLIENT_EDGE_URL + '/command/{}'.format(self.issuance_id)
        resp = self.session.delete(url)
        resp.raise_for_status()

    def is_complete(self):
        """
        Returns True if the message was successful, False if it is pending, and it will throw a
        DownlinkMessageError if the message was unsuccessful.
        """
        status = self.get_status()
        if 'Pending' in status:
            return False
        elif 'Success' in status:
            return True
        else:
            raise DownlinkMessageError(self, status)

    def wait_for_success(self):
        """
        Polls the status of the message and returns once it is successful.
        Raises a `RuntimeError` if the message is unsuccessful.
        """
        while not self.is_complete():
            sleep(CLIENT_EDGE_POLL_PERIOD_S)


class DownlinkMessageError(Exception):
    """
    Exception thrown when checking the success of a DownlinkMessage if it is
    neither successful nor pending.
    """
    pass


def parse_time(time_str):
    """ Parses a time string from Conductor into a datetime object. """
    return dateutil.parser.parse(time_str)


def format_time(dtime):
    """ Converts a `datetime` object into a string that Conductor understands. """
    return dtime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]


def flatten_status(results):
    """ Flattens the status message's 'properties' dictionary. """
    for status in results:
        status['value']['properties'] = {d['name']: d['value']
                                         for d in status['value']['properties']}
    return results


def _result_to_uplink_message(result):
    """ Converts a 'result' dictionary from Conductor to an UplinkMessage object. """

    if result['value']['avgSignalMetadata']:
        packet_signal_data = PacketSignalData(result['value']['avgSignalMetadata']['sf'],
                                              result['value']['avgSignalMetadata']['snr'],
                                              result['value']['avgSignalMetadata']['rssi'],
                                              result['value']['avgSignalMetadata']['frequency'])
    else:
        packet_signal_data = None

    port = result['value'].get('portNumber')
    if port is not None:
        port = int(port)

    return UplinkMessage(result['value']['module'], result['value']['gateway'],
                         result['value']['pld'], port,
                         parse_time(result['time']), result['uuid'],
                         result['metadata']['props'].get('net_tok'),
                         packet_signal_data)

def hexlify(buff):
    """
    We write our own version of hexlify because python 3's version returns
    a binary string that can't be converted to JSON.
    """
    if isinstance(buff, str):
        buff = (ord(x) for x in buff)
    return ''.join('{:02X}'.format(x) for x in buff)


def _handle_conductor_response(resp):
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        LOG.error("Got error from Conductor: %s", resp.content)
        raise

    return resp.json()
