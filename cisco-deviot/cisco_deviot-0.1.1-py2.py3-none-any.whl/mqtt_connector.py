# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import json

import time
from paho.mqtt.client import Client

from cisco_deviot import logger


class MqttConnector:
    def __init__(self, gateway):
        self.gateway = gateway
        self.client = Client()
        self.client.on_connect = self.__on_connect__
        self.client.on_disconnect = self.__on_disconnect__
        self.client.on_message = self.__on_message__
        self.__connected = False

    def start(self):
        self.client.connect_async(self.gateway.connector_server.hostname, self.gateway.connector_server.port, 60)
        self.client.loop_start()
        logger.info("connecting to {server} ...".format(server=self))

    def stop(self):
        self.client.disconnect()

    def __on_connect__(self, client, userdata, flags, rc):
        self.client.subscribe(self.gateway.action_topic)
        self.__connected = True
        logger.info("{server}{topic} connected".format(server=self, topic=self.gateway.action_topic))

    def __on_disconnect__(self, client, userdata, rc):
        logger.warn("{server} disconnected".format(server=self))
        self.__connected = False
        backoff = 2
        while not self.__connected:
            logger.info("reconnecting to {server} in {sec} seconds ...".format(server=self, sec=backoff))
            time.sleep(backoff)
            backoff = min(128, backoff * 2)
            try:
                self.client.reconnect()
                self.__connected = True
            except:
                pass

    def is_connected(self):
        return self.__connected

    def __on_message__(self, client, userdata, msg):
        message = str(msg.payload)
        try:
            args = json.loads(message)
            self.gateway.call_action(args)
        except Exception, error:
            logger.error("failed to process message {message}: {error}".format(message=message, error=error))

    def publish(self, data):
        json_string = json.dumps(data, sort_keys=False)
        self.client.publish(self.gateway.data_topic, json_string)

    def __str__(self):
        return "mqtt connector {server}:{port}".format(server=self.gateway.connector_server.hostname,
                                                    port=self.gateway.connector_server.port)
