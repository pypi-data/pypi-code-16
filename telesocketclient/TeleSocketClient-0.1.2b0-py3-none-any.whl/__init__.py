import json
import logging
import threading
import time

import websocket
from NucleusUtils import versions
from NucleusUtils.jProtocol.helper import parse

from TeleSocketClient import types
from TeleSocketClient.exceptions import APIException
from TeleSocketClient.request import RequestManager

VERSION = versions.Version(0, 1, 2, 'beta')
__version__ = VERSION.version

ADDRESS = 'wss://telesocket.illemius.xyz/ws'
RECONNECT_DELAY = 2

log = logging.getLogger('TeleSocket')


class TeleSocket:
    def __init__(self, address=ADDRESS, daemonic=True, start=True):
        self.address = address
        self.ws = websocket.WebSocketApp(address,
                                         on_open=self.on_open, on_close=self.on_close,
                                         on_error=self.on_error, on_message=self.on_message)
        self.daemonic = daemonic

        self.requests = RequestManager(self)
        self.session = None

        self.reconnect_delay = RECONNECT_DELAY

        self.ready = threading.Event()

        self.handlers = []

        if start:
            self.run_forever()

    def add_telegram_handler(self, handler):
        self.handlers.append(handler)

    def notify_telegram_handlers(self, data):
        for handler in self.handlers:
            handler(data)

    def on_message(self, ws, message):
        log.debug(f"Receive: '{message}'")
        data = parse(message)

        message_type = data.get('type')
        if 'id' in data:
            self.requests.response(data['id'], data)
        elif message_type == 'telegram_update':
            self.notify_telegram_handlers(data.get('data'))

    def on_error(self, ws, error):
        if isinstance(error, KeyboardInterrupt):
            return
        log.error(f"Error {error}")
        log.warning('Reconnecting...')
        timer = threading.Timer(self.reconnect_delay, self.ws.run_forever)
        timer.setDaemon(self.daemonic)
        timer.setName('TeleSocket')
        if self.reconnect_delay < 8:
            self.reconnect_delay *= 2
        timer.start()

    def on_open(self, ws):
        self.ready.set()
        log.info('Connected.')
        self.reconnect_delay = RECONNECT_DELAY
        if self.session:
            self._join_session()

    def on_close(self, ws):
        # log.warning('Disconnected.')
        pass

    def run_forever(self):
        threading.Thread(target=self.ws.run_forever, name='TeleSocket', daemon=self.daemonic).start()

    def send(self, data):
        try:
            if not self.ws.sock or not self.ws.sock.connected:
                log.debug('Trying sent to closed connection!')
                self.ready.wait(self.reconnect_delay + RECONNECT_DELAY)
                return self.send(data)
            if self.ready.is_set():
                self.ready.clear()
            return self.ws.send(json.dumps(data, separators=(',', ':')))
        except websocket.WebSocketConnectionClosedException:
            log.error('Connection closed!')

    def request(self, method, data=None, send=True):
        if data is None:
            data = {}
        return self.requests.request(method, data, send)

    def register(self, username, access_code=None):
        payload = {'username': username}
        if access_code:
            payload.update({'code': access_code})

        result = self.request('register', payload)
        return types.User.serialize(result.wait())

    def login(self, token=None, session=None):
        payload = {'token': token}
        if session:
            payload['session'] = session
        result = self.request('login', payload).wait()
        self._set_session()
        return types.User.serialize(result)

    def _set_session(self):
        self.session = self.get_session()
        log.debug(f"Open session '{self.session.id}'")

    def _join_session(self):
        def join_session():
            self.login(session=self.session.id)

        threading.Thread(target=join_session, name='RestoreSession').start()

    def get_session(self):
        result = self.request('get_session')
        return types.Session.serialize(result.wait())

    def logout(self):
        # Maybe need wait.
        self.session = None
        return self.request('logout')

    def ping(self):
        start = time.time()
        self.request('ping').wait()
        return round((time.time() - start) * 1000)

    def set_webhook(self, bot_name):
        payload = {'name': bot_name}
        result = self.request('set_webhook', payload).wait()
        return types.WebHook.serialize(**result['webhook'])

    def del_webhook(self):
        result = self.request('del_webhook').wait()
        return True
