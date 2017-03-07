"""
Control the Gecko-Profiler Add-on by sending commands to Web Socket server.
Step:
1. start Web Socket server by ServerController.start_server()
2. connect()
3. open_profiling_page()
4. get_profiling_file() or get_profiling_link()
5. disconnect()
"""

import os
import json
import time
import logging
from websocket import create_connection

from server import commands

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ONE_MINUTE = 60
ONE_HOUR = 60 * 60


class ControllerClient:

    def __init__(self, control_server=None, save_path=None):
        self.hostname = 'ws://localhost:8888/py'
        self.control_server = control_server
        self.is_online = False
        self.profile_ready = False
        self.ws_conn = None
        # default retry time 5
        self.retry_time = 5
        if save_path:
            self.save_path = save_path
        else:
            self.save_path = CURRENT_PATH
        if not save_path.endswith(os.sep):
            self.save_path += os.sep

    def set_retry_time(self, retry_time):
        if isinstance(retry_time, int) and 0 < retry_time <= 100:
            self.retry_time = retry_time
        else:
            logger.warn('Can not set retry_time to {}. (0 < retry_time <= 100)')

    def set_save_path(self, path):
        self.save_path = path

    def _ping_addon(self):
        # wait for 1 min for ping add-on
        self.ws_conn.settimeout(ONE_MINUTE)
        data = {
            commands.KEY_NAME: commands.VALUE_PING_ADDON,
            commands.KEY_DATA: ''
        }
        # retry 60 times for ping
        ping_time = 60
        for _ in range(ping_time):
            ret_code, _ = self._send_and_recv(data)
            if ret_code == commands.REPLY_STAT_SUCCESS:
                self.profile_ready = True
                return True
            logger.debug('retry ...')
            time.sleep(1)
        logger.error("Can not open profiling page.")
        return False

    def connect(self):
        logger.info('Connecting Web Socket server {} ...'.format(self.hostname))
        self.ws_conn = create_connection(self.hostname)
        self.is_online = True

        # wait for add-on online
        ret_status = self._ping_addon()
        if not ret_status:
            # offline if there is no add-on
            self.is_online = False

    def disconnect(self):
        self.ws_conn.close()

    def _force_stop_server(self):
        if self.control_server:
            self.control_server.stop_server()
        else:
            logger.warn('Cannot force stop Web Socket server.')

    def send_stop_server_command(self):
        logger.info('Stopping Web Socket server ...')
        data = {
            commands.KEY_NAME: commands.VALUE_STOP,
            commands.KEY_DATA: ''
        }
        self._send(data)
        self.is_online = False
        self.profile_ready = False
        logger.info('Stopped.')

    def open_profiling_page(self):
        # wait for 1 hour for open page
        self.ws_conn.settimeout(ONE_HOUR)
        logger.info('Opening profiling page ...')
        data = {
            commands.KEY_NAME: commands.VALUE_START,
            commands.KEY_DATA: ''
        }
        for _ in range(self.retry_time):
            ret_code, _ = self._send_and_recv(data)
            if ret_code == commands.REPLY_STAT_SUCCESS:
                self.profile_ready = True
                return True
            logger.debug('retry ...')
        logger.error("Can not open profiling page.")
        return False

    def get_profiling_file(self):
        # wait 1 hour for get profiling data file
        self.ws_conn.settimeout(ONE_HOUR)
        logger.info('Getting profiling file ...')
        data = {
            commands.KEY_NAME: commands.VALUE_GET_FILE,
            commands.KEY_DATA: self.save_path
        }
        if self.profile_ready:
            for _ in range(self.retry_time):
                ret_code, ret_msg = self._send_and_recv(data)
                if ret_code == commands.REPLY_STAT_SUCCESS:
                    return ret_msg
                logger.debug('retry ...')
            logger.error('Can not get profiling file.')
        else:
            logger.error('Profiling Data is not ready.')

    def get_profiling_link(self):
        # wait 1 hour for get profiling data link
        self.ws_conn.settimeout(ONE_HOUR)
        logger.info('Getting profiling link ...')
        data = {
            commands.KEY_NAME: commands.VALUE_GET_LINK,
            commands.KEY_DATA: ''
        }
        if self.profile_ready:
            for _ in range(self.retry_time):
                ret_code, ret_msg = self._send_and_recv(data)
                if ret_code == commands.REPLY_STAT_SUCCESS:
                    return ret_msg
                logger.debug('retry ...')
            logger.error('Can not get profiling link.')
        else:
            logger.error('Profiling Data is not ready.')

    def _send_and_recv(self, data):
        self._send(data)
        return self._recv()

    def _send(self, data):
        if not self.is_online:
            raise Exception('The client does not connect to server.')
        if isinstance(data, dict):
            message = json.dumps(data)
        else:
            message = data
        logger.debug('Sending {} ...'.format(message))
        self.ws_conn.send(message)
        logger.debug('Sent.')

    def _recv(self):
        if not self.is_online:
            raise Exception('The client does not connect to server.')
        logger.debug('Receiving...')
        try:
            result = self.ws_conn.recv()
            logger.debug('Received {}'.format(result))
            try:
                result_dict = json.loads(result)
                ret_code = result_dict.get(commands.KEY_NAME, 0)
                ret_message = result_dict.get(commands.KEY_DATA, '')
                return ret_code, ret_message
            except:
                return commands.REPLY_STAT_FAIL, 'Can not parse JSON: {}'.format(result)
        except:
            return commands.REPLY_STAT_FAIL, 'recv() timeout'
