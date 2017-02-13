# coding=utf-8
from __future__ import absolute_import, print_function, unicode_literals
from __future__ import division
import threading
from urlparse import urlparse
import json
import logging
import copy
import base64
import time
from datetime import datetime

from oauthlib.oauth2 import BackendApplicationClient

from requests_oauthlib import OAuth2Session
import validators

from proofpoint.kafka.InfobusConsumer import InfobusConsumer
from proofpoint.kafka.errors import KafkaRestError

log = logging.getLogger(__name__)


class KafkaRestConsumer(InfobusConsumer):
    """
    A Kafka rest client that consumes records from Kafka Rest Proxy (KRP). Confluent api docs are located at
    http://docs.confluent.io/2.0.0/kafka-rest/docs/api.html

    With current version of KRP, a client can consume a topic at a time, an new instance must be created for each topic

    A client subscribes to a topic by calling the subscribe(..) method. After that client has to continuously poll for
    new messages and commit.

    Usage example
            consumer = KafkaRestConsumer(group="test-group", ....)
            consumer.subscribe('test-topic')
            while True:
                try:
                    messages = consumer.poll()
                    ...
                    ...
                    consumer.commit()
                except Exception as e:
                    # handle exceptions

    The client periodically sends heartbeat pings to KRP after the poll() returns with messages until the commit() is
    called.

    Close must be called during the exit/shutdown of the client, so the consumer instance is closed on the KRP side.

    Keyword Arguments:
        group_name (str) : The name of the consumer group to join for dynamic partition assignment and to use for
            fetching and committing offsets. REQUIRED.
        client_name (str): Name for the consumer instance, which will be used in URLs for the consumer.
            This must be unique, at least within the proxy process handling the request.
            Recommended to use hostname of the client, if a client has multiple consumers in the group for
            same topic another unique id must be appended to hostname (i.e hostname-1, hostname-2 etc)
            REQUIRED.
        topic (str): Name of the topic to be consumed. REQUIRED.
        auto_commit (bool): If True , the consumer's offset will be periodically committed in the background. If False,
            client has to explicitly call the commit(). Its recommended for the client to explicitly call commit.
            Default: False.
        offset (str): A policy for resetting offsets on offset out of range errors:
            'earliest' will move to the oldest available message,
            'latest' will move to the most recent. Any other value will raise the exception.
             Default: 'latest'.
        format (str): The format of consumed messages, which is used to convert messages into a JSON-compatible form.
            Valid values: “binary”, “json”.
            Default: binary
        max_fetch_size (int) (bytes): The maximum number of bytes of unencoded keys and values that should be included in the
            response. This provides approximate control over the size of responses and the amount of memory required to 
            store the decoded response. The actual limit will be the minimum of this setting and the server-side 
            configuration consumer.request.max.bytes.
            Default: 33554432
        oauth_token_url (str): URL to get SAML oauth bridge tokens
        auth_client_id (str): OAuth client id. REQUIRED.
        auth_client_secret (str): OAuth client secret. REQUIRED.
        kafka_rest_lb (str): Kafka rest proxy load balancer URL. REQUIRED.
        read_from_krp (bool): If the client and KRP hosts are in same data center and reachable by the client, setting
            this to True, will make the client fetch data from KRP host directly with out going through load balancer
            every time for the fetch requests. If True all the read,commit,delete requests will be sent directly to
            KRP host. Use this for better latency
        heartbeat_fetch_size (int) (bytes): Number of bytes requested for heartbeat request. Clients should never set this.
            Default: 1. Any other value will cause messages being lost.
        heartbeat_interval (int) (seconds): How often should the heartbeat thread send the heartbeat request while the client is
            still processing messages.
            Default: 60
        krp_consumer_timeout (int) (seconds): Kafka Rest proxy consumer timeout. Amount of idle time before a consumer instance is
            automatically destroyed on Kafka Rest proxy
            Default: 300


    """

    DEFAULT_CONFIG = {
        'group_name': None,
        'client_name': None,
        'topic': None,
        'auto_commit': False,
        'offset': 'largest',
        'format': 'binary',
        'max_fetch_size': 33554432,
        'oauth_token_url': None,
        'auth_client_id': None,
        'auth_client_secret': None,
        'kafka_rest_lb': None,
        'read_from_krp': True,
        'heartbeat_fetch_size': 1,
        'heartbeat_interval': 60,
        'krp_consumer_timeout': 300
    }

    __config = None
    __krp_host = None
    __krp_host_port = None
    __group_url_template = '%s/consumers/%s'
    __read_topic_url_template = '%s/consumers/%s/instances/%s/topics/%s?max_bytes=%s'
    __commit_offsets_url_template = '%s/consumers/%s/instances/%s/offsets'
    __delete_consumer_url_template = '%s/consumers/%s/instances/%s'
    __group_url_headers = None
    __read_topic_url_headers = None
    __commit_offsets_url_headers = None
    __delete_consumer_url_headers = None
    __heartbeat_url_headers = None
    __heartbeat_thread = None
    __thread_event = None
    __oauth_session = None
    __last_successful_attempt = None

    def __init__(self, **configs):
        InfobusConsumer.__init__(self)
        log.debug("Starting the Kafka Rest Consumer")
        self.config = copy.copy(self.DEFAULT_CONFIG)
        for key in self.config:
            if key in configs:
                self.config[key] = configs.pop(key)

        assert self.config['group_name'] is not None or self.config['group_name'] == "", 'group name must not be empty'
        assert self.config['client_name'] is not None or self.config['client_name'] == "", \
            'client name must not be empty'
        assert self.config['oauth_token_url'] is not None or self.config['oauth_token_url'] == "", \
            'oauth_token_url must not be empty'
        assert self.config['kafka_rest_lb'] is not None or self.config['kafka_rest_lb'] == "", \
            'Kafka Rest LB must not be empty'
        assert self.config['auth_client_id'] is not None or self.config['auth_client_id'] == "", \
            'auth client id must not be empty'
        assert self.config['auth_client_secret'] is not None or self.config['auth_client_secret'] == "", \
            'auth client secret must not be empty'
        if validators.url(self.config['oauth_token_url']) is not True:
            raise ValueError('invalid url %s' % self.config['oauth_token_url'])
        if validators.url(self.config['kafka_rest_lb']) is not True:
            raise ValueError('invalid url %s' % self.config['kafka_rest_lb'])
        fetch_size = int(self.config['max_fetch_size'])
        if fetch_size < 1 * 1024 * 1024:
            raise ValueError('max_fetch_size must be greater than or equal to 1048576')
        interval = int(self.config['heartbeat_interval'])
        if not 5 <= interval <= 300:
            raise ValueError('heartbeat_interval must be in the range of 5 and 300')
        if self.config['krp_consumer_timeout'] < 5 or self.config['krp_consumer_timeout'] > 300:
            raise ValueError('krp_consumer_timeout must be in the range of 60 and 300')

        self.__oauth_session = OAuth2Session(client=BackendApplicationClient(client_id=self.config['auth_client_id']),
                                             auto_refresh_url=self.config['oauth_token_url'],
                                             token_updater=lambda token: log.debug('token updated'))
        self.__oauth_session.fetch_token(token_url=self.config['oauth_token_url'],
                                         client_id=self.config['auth_client_id'],
                                         client_secret=self.config['auth_client_secret'])

        group_url = self.__group_url_template % (self.config['kafka_rest_lb'], self.config['group_name'])
        group_headers = {'content-type': 'application/vnd.kafka.json.v1+json', 'Accept': 'application/json'}
        self.__group_url_headers = (group_url, group_headers)

    def subscribe(self, topic):
        # validate
        assert topic is not None or topic == "", 'topic must not be empty'

        self.config['topic'] = topic
        try:
            try:
                self.__krp_host, self.__krp_host_port = self.__register_consumer()

            except KafkaRestError as e:
                # client got restarted and didn't close consumer properly
                if int(e.error_code) == 40902:
                    # sleep and retry
                    time.sleep(self.config['krp_consumer_timeout'])
                    self.__krp_host, self.__krp_host_port = self.__register_consumer()
                else:
                    raise e
            self.__last_successful_attempt = datetime.now()
            self.__set_urls()
        except Exception as e:
            log.error(e)
            raise

    def __set_urls(self):
        accept_header = 'application/vnd.kafka.%s.v1+json' % (self.config['format'])
        if self.config['read_from_krp']:
            read_url = self.__read_topic_url_template % (
                self.__krp_host_port, self.config['group_name'], self.config['client_name'], self.config['topic'],
                self.config['max_fetch_size'])
            read_headers = {'Accept': accept_header}

            commit_url = self.__commit_offsets_url_template % (
                self.__krp_host_port, self.config['group_name'], self.config['client_name'])
            commit_headers = {
                'Accept': 'application/vnd.kafka.v1+json, application/vnd.kafka+json, application/json'}

            close_url = self.__delete_consumer_url_template % (
                self.__krp_host_port, self.config['group_name'], self.config['client_name'])
            close_headers = {
                'Accept': 'application/vnd.kafka.v1+json, application/vnd.kafka+json, application/json'}

            heartbeat_url = self.__read_topic_url_template % (
                self.__krp_host_port, self.config['group_name'], self.config['client_name'], self.config['topic'],
                self.config['heartbeat_fetch_size'])
            heartbeat_headers = {'Accept': accept_header}

        else:
            read_url = self.__read_topic_url_template % (
                self.config['kafka_rest_lb'], self.config['group_name'], self.config['client_name'],
                self.config['topic'], self.config['max_fetch_size'])
            read_headers = {'Accept': accept_header, 'rest-proxy-host': self.__krp_host}

            commit_url = self.__commit_offsets_url_template % (
                self.config['kafka_rest_lb'], self.config['group_name'], self.config['client_name'])
            commit_headers = {
                'Accept': 'application/vnd.kafka.v1+json, application/vnd.kafka+json, application/json',
                'rest-proxy-host': self.__krp_host}

            close_url = self.__delete_consumer_url_template % (
                self.config['kafka_rest_lb'], self.config['group_name'], self.config['client_name'])
            close_headers = {
                'Accept': 'application/vnd.kafka.v1+json, application/vnd.kafka+json, application/json',
                'rest-proxy-host': self.__krp_host}

            heartbeat_url = self.__read_topic_url_template % (
                self.config['kafka_rest_lb'], self.config['group_name'], self.config['client_name'],
                self.config['topic'],
                self.config['heartbeat_fetch_size'])
            heartbeat_headers = {'Accept': accept_header, 'rest-proxy-host': self.__krp_host}

        self.__read_topic_url_headers = (read_url, read_headers)
        self.__commit_offsets_url_headers = (commit_url, commit_headers)
        self.__delete_consumer_url_headers = (close_url, close_headers)
        self.__heartbeat_url_headers = (heartbeat_url, heartbeat_headers)

    def close(self):
        try:
            self.__stop_heartbeat()
            response = self.__oauth_session.request('delete', self.__delete_consumer_url_headers[0],
                                                    headers=self.__delete_consumer_url_headers[1],
                                                    client_id=self.config['auth_client_id'],
                                                    client_secret=self.config['auth_client_secret'])

            log.debug('delete consumer response: %s' % response.status_code)
        except Exception as e:
            # we won't get much by raising the exception as it will be called with atexit handler
            log.error(e)

    def poll(self):
        messages = []
        records = []
        try:
            self.__stop_heartbeat()

            try:
                records = self.__read_topic()
            except KafkaRestError as e:
                log.error(e)
                if int(e.error_code) == 40403:
                    # re-register and try again
                    self.__krp_host, self.__krp_host_port = self.__register_consumer()
                    records = self.__read_topic()
                elif int(e.error_code) == 502 or int(e.error_code) == 503 or int(e.error_code) == 504 or \
                                int(e.error_code) == 599:
                    delta = datetime.now() - self.__last_successful_attempt
                    if delta.total_seconds() > self.config['krp_consumer_timeout']:
                        self.__krp_host, self.__krp_host_port = self.__register_consumer()
                        records = self.__read_topic()
                else:
                    raise e

            log.debug('Fetched %s records from kafka rest' % len(records))
            for record in records:
                if self.config['format'] == 'binary':
                    message = base64.b64decode(record['value'])
                    json_message = json.loads(message, 'utf-8')
                else:
                    json_message = record['value']
                messages.append(json_message)
        except Exception as e:
            log.error(e)
            raise
        # start heartbeat timer
        self.__thread_event = threading.Event()
        self.__heartbeat_thread = HeartbeatThread(self.config['heartbeat_interval'], self.__oauth_session,
                                                  self.config['auth_client_id'], self.config['auth_client_secret'],
                                                  self.__heartbeat_url_headers[0], self.__heartbeat_url_headers[1],
                                                  self.__thread_event)
        self.__heartbeat_thread.start()
        self.__last_successful_attempt = datetime.now()
        return messages

    def commit(self):
        try:
            # close heartbeat thread if its already active
            self.__stop_heartbeat()
            self.__commit()
        except KafkaRestError as e:
            # Not really sure if we want to handle consumer not found or bad gateway exceptions here as they
            # will get handled in the poll(). Even if their was an error next commit() would move the offsets.
            # We will pass on the errors for now
            log.warn("Unable to commit offsets", e)
            if not (int(e.error_code) != 40403 and int(e.error_code) >= 500):
                raise e

    def __commit(self):
        response = self.__oauth_session.request('post', self.__commit_offsets_url_headers[0],
                                                headers=self.__commit_offsets_url_headers[1],
                                                client_id=self.config['auth_client_id'],
                                                client_secret=self.config['auth_client_secret'])
        self.__handle_errors(response)
        log.debug('Commit offsets response: %s' % response.status_code)

    def __stop_heartbeat(self):
        # close heartbeat timer if its already active
        if self.__heartbeat_thread:
            self.__thread_event.set()

    def __register_consumer(self):
        consumer_json = {'name': self.config['client_name'], 'format': self.config['format'],
                         'auto.offset.reset': self.config['offset'],
                         'auto.commit.enable': str(self.config['auto_commit']).lower()}

        log.debug("creating consumer with json" + str(consumer_json))
        response = self.__oauth_session.request('post', self.__group_url_headers[0], data=json.dumps(consumer_json),
                                                headers=self.__group_url_headers[1],
                                                client_id=self.config['auth_client_id'],
                                                client_secret=self.config['auth_client_secret'])
        log.debug("created consumer response" + response.text)

        self.__handle_errors(response)

        base_uri = response.json()["base_uri"]
        url = urlparse(base_uri)
        log.info("Created consumer on " + url.hostname)
        return url.hostname, '%s://%s' % (url.scheme, url.netloc)

    # Read messages from a topic and return them
    def __read_topic(self):
        response = self.__oauth_session.request('get', self.__read_topic_url_headers[0],
                                                headers=self.__read_topic_url_headers[1],
                                                client_id=self.config['auth_client_id'],
                                                client_secret=self.config['auth_client_secret'])

        self.__handle_errors(response)

        return response.json()

    @staticmethod
    def __handle_errors(response):
        if 400 <= response.status_code <= 500:
            # parse json if possible
            try:
                response_json = response.json()
                error_code = response_json['error_code']
                message = response_json['message']
            except Exception:
                error_code = response.status_code
                message = response.text

            raise KafkaRestError(error_code, message)
        elif response.status_code > 500:
            raise KafkaRestError(response.status_code, response.text)


class HeartbeatThread(threading.Thread):
    def __init__(self, heartbeat_interval, oauth_session, client_name, client_secret, url, headers, event):
        threading.Thread.__init__(self, args=event)
        self.heartbeat_interval = heartbeat_interval / 100
        self.oauth_session = oauth_session
        self.client_name = client_name
        self.client_secret = client_secret
        self.url = url
        self.headers = headers
        self.event = event
        self.setDaemon(True)

    def run(self):
        while not self.event.is_set():
            i = 0
            while i < 100 and not self.event.is_set():
                time.sleep(self.heartbeat_interval)
                i += 1
            if not self.event.is_set():
                self.oauth_session.request('get', self.url, headers=self.headers,
                                           client_id=self.client_name,
                                           client_secret=self.client_secret)
