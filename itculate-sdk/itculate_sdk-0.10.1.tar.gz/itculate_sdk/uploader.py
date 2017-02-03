#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#
import json
import logging
import re
import binascii
import itertools
from collections import defaultdict

import six
from unix_dates import UnixDate

from .graph import Vertex, Edge
from .dictionary import Dictionary
from .local_credentials import read_local_credentials
from .types import TypedValue
from . import __version__

_VALID_COLLECTOR_ID = re.compile(r"^[a-zA-Z0-9_]+$")
_DEFAULT_API_URL = "https://api.itculate.io/api/v1"
_DEFAULT_AGENT_REST_URL = "http://localhost:8000"
_DEFAULT_PK = "pk"
_DEFAULT_COLLECTOR_ID = "sdk"

logger = logging.getLogger(__name__)


class Payload(object):
    """
    A payload represents a single call to the ITculate Rest API (or agent) with data to upload.

    When reports from different collector ids are involved, they need to be split into separate payloads. This is
    especially important for topology payloads - where the collector ID is essential for the merge process.

    For other types of data (like timeseries, events, dictionary, ...), we can join all in a single Rest API POST (a
    single payload).

    Tenant ID is optional. If not provided, the API key will be used to determine the the tenant. If provided, the
    server side will double check that the user used to access has indeed permissions to access this tenant.
    """

    def __init__(self, collector_id, collector_version=None, tenant_id=None, **kwargs):
        assert _VALID_COLLECTOR_ID.match(collector_id), "Invalid collector ID (must be [a-zA-Z0-9_]+)"
        self._tenant_id = tenant_id
        self._collector_id = collector_id
        self._collector_version = collector_version or __version__
        self._data = kwargs

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def collector_id(self):
        return self._collector_id

    @property
    def collector_version(self):
        return self._collector_version

    @property
    def data(self):
        return self._data

    def __getitem__(self, item):
        return self._data[item]


class PayloadGenerator(object):
    """
    Derivatives of this class hold the transient state of each of the data types. When 'flush' is called, a payload
    is generated with the local data inside.
    """

    def __init__(self, collector_id, tenant_id=None):
        self._collector_id = collector_id
        self._tenant_id = tenant_id

    def flush(self):
        """ :rtype: Payload """
        raise NotImplementedError()

    @property
    def collector_id(self):
        return self._collector_id

    @property
    def tenant_id(self):
        return self._tenant_id

    def __str__(self):
        return self.__class__.__name__


class TopologyPayloadGenerator(PayloadGenerator):
    """
    Topology report is different for different collector IDs. Because of that, each topology is stored in its own
    payload, sent separately to the server.
    """

    def __init__(self, collector_id, tenant_id=None):
        """
        :param str tenant_id: (optional) Tenant ID. If not provided, tenant ID will be extracted from user data
        :param str collector_id: Unique (within tenant) name for this topology
        """
        super(TopologyPayloadGenerator, self).__init__(collector_id, tenant_id)
        assert collector_id, "Collector id must be provided"

        self._collector_id = collector_id
        self._vertices_by_pk = {}
        self._edges = []

    def __str__(self):
        return "{}-{}".format(self.__class__.__name__, self._collector_id)

    def add_vertex(self,
                   vertex_type,
                   name,
                   keys,
                   primary_key_id=None,
                   counter_types=None,
                   data=None,
                   **kwargs):
        """
        Adds a vertex to the topology

        :param str vertex_type: Vertex type
        :param str primary_key_id: Name of key (within 'keys') designated as primary key (must be globally unique)
        :param dict[str,str]|str keys: A set of unique keys identifying this vertex. If str, 'pk' will be used as key
        :param str name: Name for vertex
        :param dict[str,DataType] counter_types: (optional) mapping of the different counters reported by this vertex
        :param dict data: Set of initial values to assign to vertex (optional)
        :param kwargs: Any additional key:value pairs that should be assigned to vertex.
        :rtype: Vertex
        """

        if isinstance(keys, str) or isinstance(keys, unicode):
            assert primary_key_id is None or primary_key_id == "pk", \
                "Expecting primary_key_id to be None or 'pk' when providing keys as a str"
            keys = {"pk": keys}
            primary_key_id = "pk"

        else:
            primary_key_id = primary_key_id or keys.keys()[0]

        v = Vertex(vertex_type=vertex_type,
                   name=name,
                   keys=keys,
                   primary_key_id=primary_key_id,
                   data=data,
                   **kwargs)

        self.update(vertices=[v])

        if counter_types is not None:
            for counter, data_type in six.iteritems(counter_types):
                Dictionary.update_data_type(dictionary_type=Dictionary.D_TYPE_TIMESERIES,
                                            vertex_key=v.first_key,
                                            attribute=counter,
                                            data_type=data_type)

        return v

    def connect(self, source, target, topology):
        """
        Connect (create an edge between) two (or two sets of) vertices.
        Vertices are identified by either providing the Vertex object or only their keys.

        If source / target is a list of vertices (or keys), this will create a set of edges between all sources and all
        targets

        :param source: Identify source/s
        :type source: str|dict|Vertex|collections.Iterable[dict]|collections.Iterable[Vertex]|collections.Iterable[str]
        :param target: Identify target/s
        :type target: str|dict|Vertex|collections.Iterable[dict]|collections.Iterable[Vertex]|collections.Iterable[str]
        :param str topology: Topology (edge type) to use for this connection
        """

        assert '$' not in topology, "Invalid topology value '{}', should not contain '$'".format(topology)

        source = source if isinstance(source, list) else [source]
        target = target if isinstance(target, list) else [target]

        edges = []
        for sk, tk in itertools.product(source, target):
            if isinstance(sk, str):
                sk = {"pk": sk}

            if isinstance(tk, str):
                tk = {"pk": tk}

            edges.append(Edge(edge_type=topology, source=sk, target=tk))

        self.update(edges=edges)

    def update(self, vertices=None, edges=None):
        """
        Update the uploader with new information.

        :param collections.Iterable[Vertex] vertices: Collection of vertices
        :param collections.Iterable[Edge] edges: Collection of edges
        """
        assert vertices or edges, "No data provided"

        if vertices:
            self._vertices_by_pk.update({v.first_key: v.freeze() for v in vertices})

        if edges:
            self._edges.extend(edges)

    def flush(self):
        """
        Called is when the builder of the topology is ready for it to be uploaded. All the vertices and edges are in
        and no further modifications are necessary.

        After this call, the internal state will be cleared (ready for building a new report).

        Be careful not to call flush unless the full data is populated. The ITculate server expects full reports to be
        made for the topology.

        :return: A Payload object with the topology - ready to be uploaded, None if nothing to flush
        :rtype: Payload
        """
        local_vertices_by_pk, self._vertices_by_pk = (self._vertices_by_pk, {})
        local_edges, self._edges = (self._edges, [])

        if not local_vertices_by_pk and not local_edges:
            return None

        return Payload(collector_id=self.collector_id,
                       tenant_id=self.tenant_id,
                       vertices=[v.document for v in local_vertices_by_pk.values()],
                       edges=[e.document for e in local_edges])


class GlobalPayloadGenerator(PayloadGenerator):
    def __init__(self, tenant_id=None):
        # The global payload will be reported under the 'default' collector ID.
        super(GlobalPayloadGenerator, self).__init__(_DEFAULT_COLLECTOR_ID, tenant_id)

        self._samples = defaultdict(lambda: defaultdict(list))

        self._mappings = defaultdict(list)  # type: dict[unicode, list[tuple]]
        self._mappings_changed = False

        self._events = []

    def add_counter_samples(self, vertex, counter, timestamp_to_value):
        """
        Add a set of time-series samples associated with a vertex or a key.

        If values are typed (TypedValue), the appropriate dictionary updates will be made based on these values.

        :param Vertex|str vertex: Vertex object or vertex key, if None, non_vertex_key will be used
        :param str counter: Counter name
        :param timestamp_to_value: An iterable of timestamps and values
        :type timestamp_to_value: collections.Iterable[(float, float|TypedValue)]
        """

        if isinstance(vertex, Vertex):
            vertex = vertex.first_key

        def convert_sample((ts, value)):
            stripped_value = Dictionary.update_and_strip(dictionary_type=Dictionary.D_TYPE_TIMESERIES,
                                                         vertex_key=vertex,
                                                         attribute=counter,
                                                         value=value)
            return ts, stripped_value

        self._samples[vertex][counter].extend(itertools.imap(convert_sample, timestamp_to_value))

    def map_statsd_counter_to_vertices(self, statsd_keys, vertex_counters):
        """
        Allows mapping more than one vertex counter to a set of stasd keys (host, counter, tags).

        This will replace any existing mapping for that set of statsd keys

        :param statsd_keys: Set of arbitrary values identifying this vertex (for mapping back to vertex)
        :type statsd_keys: tuple[str]|list[str]
        :param collections.Iterable[Vertex|str, str, DataType] vertex_counters: Iterable over counter identifiers
        """

        assert isinstance(statsd_keys, tuple), "'statsd_keys' must be a tuple"

        vertex_counter_identifiers = []

        for vertex, counter, data_type in vertex_counters:
            if isinstance(vertex, Vertex):
                vertex_key = vertex.first_key

            else:
                vertex_key = vertex

            if data_type is not None:
                # Update dictionary with this type!
                Dictionary.update_data_type(dictionary_type=Dictionary.D_TYPE_TIMESERIES,
                                            vertex_key=vertex_key,
                                            attribute=counter,
                                            data_type=data_type)

            vertex_counter_identifiers.append((vertex_key, counter,))

            self._mappings[self._generate_key(statsd_keys)] = vertex_counter_identifiers
            self._mappings_changed = True

    def lookup(self, statsd_keys, default_vertex_key=None):
        """
        Resolves a tuple of statsd keys to its associated vertex key

        :param statsd_keys: Set of arbitrary values identifying this vertex (for mapping back to vertex)
        :type statsd_keys: tuple[str]|list[str]
        :param str default_vertex_key: If provided, samples will associated with this vertex when lookup fails
        :rtype: (str, str)
        :return: tuple (vertex_key, counter) or None if no association found
        """
        assert isinstance(statsd_keys, (tuple, list)), "'statsd_keys' must be a tuple or list"

        key = self._generate_key(statsd_keys)
        mappings = self._mappings.get(key)

        if mappings is None and default_vertex_key is not None:
            # Lookup failed, map to the default vertex (keep vertex_type None - because there is no meta-data)
            # We will use the key as the counter name
            mappings = [(default_vertex_key, key,)]

        return mappings

    def vertex_event(self, vertex, message, event_type="MESSAGE", severity="INFO", timestamp=None):
        """
        Generic event

        :param Vertex|str vertex: Vertex (or vertex key) associated with event
        :param str severity: One of CRITICAL / ERROR / WARNING / INFO / SUCCESS
        :param str event_type: A free text with event type
        :param str message: A free text describing the event
        :param float timestamp: An optional time of event (defaults to now)
        """
        self._events.append({
            "vertex_key": vertex.first_key if isinstance(vertex, Vertex) else vertex,
            "event_time": timestamp or UnixDate.now(),
            "event_type": event_type,
            "severity": severity,
            "message": message,
        })

    @staticmethod
    def _generate_key(non_vertex_keys):
        """
        Convert the set of keys to a string (sort them first) to allow consistent hashing

        :rtype: unicode
        """
        return six.u("|".join(sorted(non_vertex_keys)))

    def flush(self):
        """
        Called is when the reported is ready to report the timeseries accumulated since last time.
        After this call, the internal state will be cleared (ready for building a new report).

        :return: A Payload object with the timeseries - ready to be uploaded
        :rtype: Payload
        """
        local_samples, self._samples = (self._samples, defaultdict(lambda: defaultdict(list)))
        local_dictionary = Dictionary.flush()
        local_mappings = self._mappings if self._mappings_changed else {}
        self._mappings_changed = False
        local_events, self._events = (self._events, [])

        # Send items as list of pairs (to avoid json serialization issues)
        return Payload(tenant_id=self.tenant_id,
                       collector_id=self.collector_id,
                       samples=local_samples,
                       dictionary=local_dictionary,
                       mappings=local_mappings.items(),
                       events=local_events)


class ProviderRegister(type):
    registry = {}

    def __new__(mcs, name, bases, attrs):
        new_cls = type.__new__(mcs, name, bases, attrs)

        if name != "Provider":
            mcs.registry[name] = new_cls

        return new_cls


class Provider(object):
    __metaclass__ = ProviderRegister

    def __init__(self, settings):
        self.settings = settings
        self.host = settings.get("host")

        self._name_to_payload_generator = {}

    @classmethod
    def factory(cls, settings):
        provider_class_name = settings.get("provider", "SynchronousApiUploader")
        assert provider_class_name in ProviderRegister.registry, \
            "provider can be one of {}".format(ProviderRegister.registry.keys())

        provider_class = ProviderRegister.registry[provider_class_name]
        return provider_class(settings)

    def handle_payload(self, payload):
        raise NotImplementedError()

    def flush_now(self, payload_generators):
        """
        Sends all unsent data without waiting

        :param: collections.Iterable[PayloadProvider]: iterable to allow us to get all payloads to flush
        :return: number of payloads flushed
        """
        count = 0

        for payload_generator in payload_generators:
            payload = payload_generator.flush()
            if payload is not None:
                self.handle_payload(payload)
                count += 1

        return count


class AgentForwarder(Provider):
    """
    Forward payloads over HTTP to the ITculate agent.

    This is typically used to forward topology, dictionary and mappings.

    Time series samples are typically forwarded using the 'statsd' protocol (via UDP) and the agent will use the
    mappings to convert these samples to ITculate time series sample objects.

    Expected settings:
        provider:               "AgentForwarder"
        host:                   (will default to hostname)
        server_url:             (defaults to 'http://127.0.0.1:8000/upload')
    """

    def __init__(self, settings):
        super(AgentForwarder, self).__init__(settings)
        self.server_url = settings.get("server_url", _DEFAULT_AGENT_REST_URL)

        import requests
        self.session = requests.session()
        self.session.verify = True
        self.session.headers["Content-Type"] = "application/json"
        self.session.headers["Accept"] = "application/json"

    def handle_payload(self, payload):
        """
        Sends (over TCP) the payload to the agent. This is supposed to end as quickly as possible and take as little
        overhead as possible from the client side

        :type payload: Payload
        """
        data_to_upload = {
            "tenant_id": payload.tenant_id,
            "collector_id": payload.collector_id,
            "collector_version": payload.collector_version,
            "host": self.host,
        }

        # Add the payload flat with the data (don't compress or pack)
        data_to_upload.update(payload.data)

        # Use the 'agent_api' attribute to figure out where to route this payload
        r = self.session.post("{}/upload".format(self.server_url),
                              data=json.dumps(data_to_upload),
                              headers={"Content-Type": "application/json"})
        r.raise_for_status()

        return r.json()


class SynchronousApiUploader(Provider):
    """
    Upload a payload to an ITculate REST API server.
    This is used to upload immediately the payload. For better performance, use the ITculate agent instead.

    Expected settings:
        provider:               "SynchronousApiUploader"
        host:                   (will default to hostname)
        server_url:             (will default to public REST API)
        https_proxy_url         (if applicable URL (including credentials) for HTTPS proxy)
        api_key:                (will try to use local credentials if not provided)
        api_secret:             (will try to use local credentials if not provided)
    """

    def __init__(self, settings):
        super(SynchronousApiUploader, self).__init__(settings)

        self.api_key = self.settings.get("api_key")
        self.api_secret = self.settings.get("api_secret")
        self.server_url = self.settings.get("server_url", _DEFAULT_API_URL)
        self.https_proxy_url = self.settings.get("https_proxy_url")

        if self.api_key is None or self.api_secret is None:
            # Read permissions from local file (under ~/.itculate/credentials)
            self.api_key, self.api_secret = read_local_credentials(role="upload",
                                                                   home_dir=self.settings.get("home_dir"))

        assert self.api_key and self.api_secret, \
            "API key/secret have to be provided (either in config or in local credentials file)"

    def handle_payload(self, payload):
        """
        Upload a payload to ITculate API

        :param Payload payload: payload to upload
        """

        # Only now import the requirements for sending data to the cloud
        import msgpack
        import zlib
        from .connection import ApiConnection
        connection = ApiConnection(api_key=self.api_key,
                                   api_secret=self.api_secret,
                                   server_url=self.server_url,
                                   https_proxy_url=self.https_proxy_url)

        data_to_upload = {
            "tenant_id": payload.tenant_id,
            "collector_id": payload.collector_id,
            "collector_version": __version__,
            "host": self.host,
            "compressed_payload": binascii.hexlify(zlib.compress(msgpack.dumps(payload.data))),
        }

        return connection.post("upload", json_obj=data_to_upload)


class InMemory(Provider):
    """
    Used by the agent as a buffer to hold accumulated data in-memory before sending it.

    Expected settings:
        provider:               "StoreInMemory"
    """

    def __init__(self, settings):
        super(InMemory, self).__init__(settings)
        self._payloads = {}  # type: dict[tuple, Payload]

    def handle_payload(self, payload):
        """
        Sends (over TCP) the payload to the agent. This is supposed to end as quickly as possible and take as little
        overhead as possible from the client side

        :type payload: Payload
        """

        payload_key = (payload.tenant_id, payload.collector_id)
        self._payloads[payload_key] = payload

    def pop(self):
        """
        Gets (and removes) the data stored in memory (called by the agent when it is time to upload data)

        :rtype: list[Payload]
        """

        local_payloads, self._payloads = (self._payloads, {})
        return local_payloads.values()
