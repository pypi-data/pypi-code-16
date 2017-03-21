import time
from threading import Event
from Queue import Queue

import logging
import logging.handlers

# pip install paho-mqtt
import paho.mqtt.client as paho
# pip install cachetools
from cachetools import LRUCache

import json
import hashlib
import uuid
from digimat.crypto import AESCipher
from digimat.crypto import XORCipher


class MQTTPayloadCipher(object):
    def __init__(self, passphrase):
        self._maxLagAllowed=0
        self._hashCache=None
        self._cipher=None
        try:
            self.onInitCipher(passphrase)
        except:
            pass

    def enableReplayAttackDetection(self, lag=60, cache=256):
        self._maxLagAllowed=lag
        self._hashCache=LRUCache(cache)

    # to be overriden
    def onInitCipher(self, passphrase):
        self._cipher=None

    def addDataEntropy(self, jdata):
        pass

    def hash_sha224(self, data):
        return hashlib.sha224(data).hexdigest()

    def hash_md5(self, data):
        return hashlib.md5(data).hexdigest()

    def encrypt(self, data):
        try:
            if data:
                jdata={'data': data, 'tstamp': time.time()}
                self.addDataEntropy(jdata)
                return self._cipher.encrypt(json.dumps(jdata))
        except:
            pass
        return None

    def decrypt(self, data):
        try:
            if data:
                # replay attack prevention by data hash check
                if self._hashCache:
                    h=self.hash_sha224(data)
                    try:
                        if self._hashCache[h]:
                            return None
                    except:
                        self._hashCache[h]=1

                # will abort by exception id data is not json formatted
                data=json.loads(self._cipher.decrypt(data))

                # replay attack prevention check by time lag detection
                if self._maxLagAllowed>0:
                    try:
                        tmsg=data['tstamp']
                        if tmsg>0:
                            tlag=abs(time.time()-tmsg)
                            if tlag>self._maxLagAllowed:
                                return None
                    except:
                        pass

                return data['data']
        except:
            pass
        return None


class MQTTPayloadAESCipher(MQTTPayloadCipher):
    def onInitCipher(self, passphrase):
        self._cipher=AESCipher(passphrase)


class MQTTPayloadXORCipher(MQTTPayloadCipher):
    def onInitCipher(self, passphrase):
        self._cipher=XORCipher(passphrase)

    def addDataEntropy(self, jdata):
        jdata['entropy']= str(uuid.uuid4().get_hex().upper()[0:12])


class MQTTPayload(object):
    def __init__(self, item, watchdogDelay=180, watchdogData=None, cipher=None):
        self._item=item
        self._value=None
        self._data=None
        self._stampValue=time.time()
        self._watchdogDelay=watchdogDelay
        self._watchdogData=watchdogData
        self._isError=False
        self._cipher=cipher

    @property
    def item(self):
        return self._item

    @property
    def client(self):
        return self.item.client

    @property
    def logger(self):
        return self.item.logger

    @property
    def data(self):
        return self._data

    @property
    def value(self):
        return self._value

    # to be overriden
    def validateData(self, data):
        return True

    def signalUpdate(self):
        self.item.signalUpdate()

    def age(self):
        return time.time()-self._stampValue

    def setWatchdog(self, delay=180, data=None):
        self._watchdogDelay=delay
        self._watchdogData=data

    def disbaleWatchdog(self):
        self._watchdogDelay=0

    def resetFailData(self):
        self._failData=None

    def isError(self):
        return self._isError

    def isValid(self):
        if not self.isError():
            if self.value is not None:
                return True

    def loadWatchdogData(self):
        data=self._watchdogData
        if data is not None and self.validateData(data):
            value=self.decodeData(data)
            if value is not None:
                self._data=data
                self._value=value

        self._isError=True
        self.signalUpdate()

    def encrypt(self, data):
        if self._cipher:
            return self._cipher.encrypt(data)
        return data

    def decrypt(self, data):
        if self._cipher:
            return self._cipher.decrypt(data)
        return data

    def loadData(self, data):
        data=self.decrypt(data)
        if data is not None and self.validateData(data):
            value=self.decodeData(data)
            if value is not None:
                # self.logger.debug('[%s]' % (self.item.topic))
                self._data=data
                self._stampValue=time.time()
                if value != self._value or self._isError:
                    self._isError=False
                    self._value=value
                    self.signalUpdate()
                    return True

    def slowManager(self):
        if not self._isError and self._watchdogDelay>0:
            if self.age()>=self._watchdogDelay:
                self.logger.warning('[%s] watchdog!' % self.item.topic)
                self.loadWatchdogData()

    # to be overriden
    def decodeData(self, data):
        return data

    def toString(self, data=None):
        try:
            if data is None:
                data=self.value
            return str(data)
        except:
            pass

    def toBoolean(self, data=None):
        try:
            if data is None:
                data=self.value
            data=data.toString().lower().strip()
            if data in ['false', '0', 'no', 'off']:
                return False
            if data in ['true', '1', 'yes', 'on']:
                return True
        except:
            pass

    def toFloat(self, data=None):
        try:
            if data is None:
                data=self.value
            return float(data)
        except:
            pass

    def toInteger(self, data=None):
        try:
            if data is None:
                data=self.value
            return int(data)
        except:
            pass

    def setCipher(self, cipher):
        self._cipher=cipher

    def setAESCipher(self, passphrase):
        self.setCipher(MQTTPayloadAESCipher(passphrase))


class MQTTPayloadBool(MQTTPayload):
    def decodeData(self, data):
        return self.toBoolean(data)

    def set(self, state):
        data='0'
        if state:
            data='1'
        super(MQTTPayloadBool, self).set(data)


class MQTTItem(object):
    def __init__(self, client, topic, qos=0, retain=False, payload=None):
        self._client=client
        self._topic=topic
        self._qos=int(qos)
        self._retain=bool(retain)
        self._eventSubscribe=Event()
        self._pendingData=None

        if payload is None:
            payload=MQTTPayload(self)
        self._payload=payload

        self.logger.info('item [%s] qos=%d created' % (topic, qos))
        self.subscribe()

    @property
    def client(self):
        return self._client

    @property
    def logger(self):
        return self._client.logger

    @property
    def topic(self):
        return self._topic

    @property
    def payload(self):
        return self._payload

    def signalUpdate(self):
        self.logger.debug('item [%s] updated (%s)' % (self.topic, self.payload.data))
        self.client.signalUpdatedItem(self)

    def subscribe(self):
        self._eventSubscribe.set()
        self.client.signalItemPendingManager(self)

    def publish(self, data):
        if data and self.payload.validateData(data):
            self._pendingData=self.payload.toString(data)
            self.client.signalItemPendingManager(self)

    # useful to cancel retained message
    def publishNull(self):
        self._pendingData=''
        self.client.signalItemPendingManager(self)

    def manager(self):
        if self._pendingData:
            data=self.payload.encrypt(self._pendingData)
            if self.client.publish(self.topic, data, self._qos, self._retain):
                self._pendingData=None
            else:
                self.client.signalItemPendingManager(self)

        if self._eventSubscribe.isSet():
            if self.client.subscribe(self.topic, self._qos):
                self._eventSubscribe.clear()
            else:
                self.client.signalItemPendingManager(self)

    def slowManager(self):
        self.payload.slowManager()

    def setAESCipher(self, passphrase):
        return self.payload.setAESCipher(passphrase)


class MQTTClient(object):
    def __init__(self, host=None, port=1883, userName=None, userPassword=None, logServer='localhost', logLevel=logging.DEBUG):
        self._cid=None
        self._host=host
        self._port=port
        self._transport='tcp'
        self._endPointUrlPath=None
        self._userName=None
        self._userPassword=None
        self._tlsCertificateFile=None
        self._cleanSession=True
        self._client=None
        self._connected=False
        self._timeoutConnect=0
        self._timeoutCreate=0
        self._eventStop=Event()

        logger=logging.getLogger("MTTQ(%s:%d)" % (self._host, self._port))
        logger.setLevel(logLevel)
        socketHandler = logging.handlers.SocketHandler(logServer, logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(socketHandler)
        self._logger=logger

        self._topicRoot=None
        self._items=[]
        self._indexItemFromTopic={}
        self._queuePendingItemsManager=Queue()
        self._queueUpdatedItems=Queue()

        self.setUser(userName, userPassword)

    @property
    def logger(self):
        return self._logger

    def setClientId(self, cid, cleanSession=False):
        self._cid=cid
        self._cleanSession=cleanSession

    def setUser(self, name, password):
        self._userName=name
        self._userPassword=password

    def setTLSCertificate(self, cfile='addtrustexternalcaroot.crt'):
        self._tlsCertificateFile=cfile

    def setTransporOverTcp(self, endPointUrlPath=None):
        self._transport='tcp'
        self._endPointUrlPath=endPointUrlPath

    def setTransportOverWebsockets(self, endPointUrlPath=None):
        self._transport='websockets'
        self._endPointUrlPath=endPointUrlPath

    def setRootTopic(self, topic):
        self._topicRoot=topic

    def items(self):
        return self._items

    def signalItemPendingManager(self, item):
        try:
            if item and item not in self._queuePendingItemsManager.queue:
                self._queuePendingItemsManager.put(item)
        except:
            pass

    def signalUpdatedItem(self, item):
        try:
            if item and item not in self._queueUpdatedItems.queue:
                self._queueUpdatedItems.put(item)
        except:
            pass

    def getNextItemUpdated(self):
        try:
            return self._queueUpdatedItems.get_nowait()
        except:
            pass

    def buildTopic(self, topic):
        if topic:
            if not self._topicRoot:
                return topic
            return '/'.join([self._topicRoot, topic])

    def validateTopic(self, topic):
        if not topic:
            return False
        if '+' in topic or '#' in topic:
            self.logger.warning('illegal char for item topic [%s]' % topic)
            return False
        try:
            # avoid topic content errors at paho level
            topic.encode('utf-8')
        except:
            return None
        return True

    def subscribeToRootTopic(self, qos=0):
        if self._topicRoot:
            topic=self.buildTopic('#')
            return self.subscribe(topic, qos)

    def itemFromTopic(self, topic):
        try:
            return self._indexItemFromTopic[topic]
        except:
            pass

    def item(self, topic):
        return self.itemFromTopic(topic)

    def createItem(self, topic, qos=0, payload=None):
        if topic:
            item=self.itemFromTopic(topic)
            if not item and self.validateTopic(topic):
                item=MQTTItem(self, topic, qos, payload)
                self._items.append(item)
                self._indexItemFromTopic[topic]=item
                self.logger.debug('now %d items' % len(self._items))
            return item

    def createItemUnderRootTopic(self, topic, qos=0, payload=None):
        return self.createItem(self.buildTopic(topic), qos, payload)

    def syncItems(self, force=True):
        for item in self._items:
            if item._eventSubscribe.isSet() or force:
                item.subscribe()

    def client(self):
        if self._client:
            return self._client
        if time.time()>self._timeoutCreate:
            self._timeoutCreate=time.time()+10.0
            try:
                self.logger.debug('creating mqtt-paho client (transport=%s)' % self._transport)
                client=paho.Client(client_id=self._cid, clean_session=self._cleanSession, transport=self._transport)

                # register callbacks
                client.on_connect=self._callbackOnConnect
                client.on_disconnect=self._callbackOnDisconnect
                client.on_subscribe=self._callbackOnSubscribe
                client.on_unsubscribe=self._callbackOnUnsubscribe
                client.on_publish=self._callbackOnPublish
                client.on_message=self._callbackOnMessage

                # comment to disable paho-mqtt logging
                # client.on_log=self._callbackOnLog

                if self._userName:
                    self.logger.info('using broker user [%s]' % self._userName)
                    client.username_pw_set(self._userName, self._userPassword)
                if self._tlsCertificateFile:
                    self.logger.info('using TLS certificate file [%s]' % self._tlsCertificateFile)
                    client.tls_set(self._tlsCertificateFile)
                if self._endPointUrlPath:
                    client.endpoint_url_path_set(self._endPointUrlPath)

                self._connected=False
                self._client=client
                return self._client
            except:
                self.logger.exception('client()')

    def isConnected(self):
        if self._client:
            if self._connected:
                return True

    def connect(self):
        if self.isConnected():
            return self._client

        if time.time()>self._timeoutConnect:
            self._timeoutConnect=time.time()+15
            self._eventStop.clear()
            try:
                client=self.client()
                if client:
                    self.logger.info('connecting to broker %s:%d over %s...' % (self._host, self._port, self._transport))
                    client.connect(self._host, self._port, keepalive=30, bind_address='')
            except:
                self.logger.exception('connect()')

    def _callbackOnConnect(self, client, userdata, flags, rc):
        self.logger.info('connect(%d)' % rc)
        if rc == 0:
            self._connected=True
            try:
                self.onConnect()
            except:
                self.logger.exception('onConnect')
            self.syncItems(True)
        else:
            # 1: Connection refused - incorrect protocol version
            # 2: Connection refused - invalid client identifier
            # 3: Connection refused - server unavailable
            # 4: Connection refused - bad username or password
            # 5: Connection refused - not authorised
            # 6-255: Currently unused.
            self.logger.error('unable to connect (code=%d)' % rc)
            self._timeoutConnect=time.time()+60
            self._connected=False

    def onConnect(self):
        pass

    def _callbackOnDisconnect(self, client, userdata, rc):
        self.logger.info('disconnect(%d)' % rc)
        self._connected=False
        try:
            self.onDisconnect()
        except:
            self.logger.exception('onDisconnect')

    def onDisconnect(self):
        pass

    def _callbackOnLog(self, client, userdata, level, buf):
        if level==paho.MQTT_LOG_ERR:
            self.logger.error(buf)
        elif level==paho.MQTT_LOG_WARNING:
            self.logger.warning(buf)
        elif level in (paho.MQTT_LOG_NOTICE, paho.MQTT_LOG_INFO):
            self.logger.info(buf)
        else:
            self.logger.debug(buf)

    def _callbackOnSubscribe(self, client, userdata, mid, granted_qos):
        pass

    def _callbackOnUnsubscribe(self, client, userdata, mid):
        pass

    def _callbackOnPublish(self, client, userdata, mid):
        pass

    def _callbackOnMessage(self, client, userdata, message):
        # self.logger.debug('onMessage(%s) qos=%d retain=%d (%d bytes)' %
        #        (message.topic, message.qos, message.retain,
        #         len(message.payload)))

        try:
            item=self.itemFromTopic(message.topic)
            if item:
                self.logger.debug('%s->onMessage(%s)' % (message.topic, message.payload))
                item.payload.loadData(message.payload)
                # stop message propagation if item found
                return
        except:
            self.logger.exception('item data load')

        try:
            self.onMessage(message.topic, message.payload, message.qos, message.retain)
        except:
            self.logger.exception('onMessage')

    def onMessage(self, topic, data, qos, retain):
        pass

    def onItemUpdated(self, item):
        pass

    def stop(self):
        if not self._eventStop.isSet():
            self.logger.info('Stop!')
            self._eventStop.set()

    def disconnect(self):
        self.stop()
        client=self.client()
        try:
            self.logger.info('disconnect()')
            client.disconnect()
        except:
            pass
        self._connected=False

    def subscribe(self, topic='#', qos=0):
        client=self.client()
        if client and self.isConnected():
            try:
                self.logger.debug('subscribe(%s)' % (topic))
                if client.subscribe(topic, qos):
                    return True
            except:
                self.logger.exception('subscribe')

    def publish(self, topic, data, qos=0, retain=False):
        client=self.client()
        if client and self.isConnected():
            try:
                self.logger.debug('publish(%s)->%s' % (topic, data))
                if client.publish(topic, data, qos, retain):
                    return True
            except:
                self.logger.exception('publish')

    def loop(self, timeout=0.1):
        self.connect()
        client=self.client()
        if client:
            client.loop(timeout=timeout)

        while self.isConnected():
            try:
                item=self._queuePendingItemsManager.get_nowait()
                if item:
                    item.manager()
            except:
                break

            try:
                item=self._queueUpdatedItems.get_nowait()
                if item:
                    try:
                        self.onItemUpdated(item)
                    except:
                        pass
            except:
                break

        if self._items:
            count=16
            while count>0:
                count-=1
                try:
                    item=self._items[self._currentItem]
                    try:
                        item.slowManager()
                    except:
                        pass
                    self._currentItem+=1
                except:
                    self._currentItem=0

    def manager(self):
        try:
            self.loop()
        except KeyboardInterrupt:
            self.disconnect()
        except:
            self.logger.exception('manager()')

    def serveForEver(self):
        try:
            while not self._eventStop.isSet():
                self.manager()
        except KeyboardInterrupt:
            self.disconnect()
        except:
            pass


if __name__ == "__main__":
    pass
