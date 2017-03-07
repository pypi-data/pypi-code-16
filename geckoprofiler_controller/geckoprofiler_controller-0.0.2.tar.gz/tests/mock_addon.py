import os
import json
import thread
import logging
import websocket

from geckoprofiler_controller.server import commands

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MockAddon:
    def __init__(self):
        self.ws = websocket.WebSocketApp('ws://localhost:8888/addon',
                                         on_open=MockAddon.on_open,
                                         on_message=MockAddon.on_message,
                                         on_error=MockAddon.on_error,
                                         on_close=MockAddon.on_close,
                                         )

    @staticmethod
    def on_message(ws, message):
        try:
            msg_obj = json.loads(message)
            # Add-on will not get commands.VALUE_PING_ADDON and VALUE_STOP.
            # It is Web Socket server duty.
            logger.debug('Add-on Get Message {}'.format(msg_obj))
            if msg_obj.get(commands.KEY_NAME) == commands.VALUE_START:
                # Start command for open profiling page
                ret_obj = {
                    'data': 'okay',
                    'command': 0
                }
                ws.send(json.dumps(ret_obj))

            elif msg_obj.get(commands.KEY_NAME) == commands.VALUE_GET_FILE:
                # GetFile command for getting profiling file
                filepath = msg_obj.get(commands.KEY_DATA)
                filename = os.path.join(filepath, 'FirefoxProfile.json.gz')
                ret_obj = {
                    'data': filename,
                    'command': 0
                }
                ws.send(json.dumps(ret_obj))

            elif msg_obj.get(commands.KEY_NAME) == commands.VALUE_GET_LINK:
                # GetFile command for getting profiling file
                ret_obj = {
                    'data': 'https://perfht.ml/2lQhjU8',
                    'command': 0
                }
                ws.send(json.dumps(ret_obj))
            else:
                logger.error('Message {} has unknown command.'.format(msg_obj))
        except:
            logger.error('Message {} is not JSON.'.format(message))

    @staticmethod
    def on_error(ws, error):
        logger.error('Error: {}'.format(error))

    @staticmethod
    def on_close(ws):
        pass

    @staticmethod
    def on_open(ws):
        pass

    @staticmethod
    def run_addon(handler):
        handler.run_forever()

    def stop_addon(self):
        self.ws.close()
        logger.info('[MockAddon] Stopped.')

    def start_addon(self):
        logger.info('[MockAddon] Starting ...')
        thread.start_new_thread(MockAddon.run_addon, (self.ws,))
        logger.info('[MockAddon] Started.')
