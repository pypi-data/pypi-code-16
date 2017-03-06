import pickle
import socket
import ssl

from .exceptions import BotSocketWrapperException
from .settings import ALLOWED_HOSTS, CONNECTIONS_IN_QUEUE, LISTEN_IP, PORT
from .utils import get_data_info, get_logger, recv_by_chunks, send_by_chunks


class Server:
    def __init__(self,
                 allowed_hosts=ALLOWED_HOSTS,
                 certfile='cert.pem',
                 logfile='logging.yml',
                 callback=lambda: None):
        self.allowed_hosts = allowed_hosts
        self.certfile = certfile
        self.logger = get_logger(__name__, logfile)
        self.callback = callback

    def serve_forever(self, listen_ip=LISTEN_IP, port=PORT):
        bot_sock = socket.socket()
        bot_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ssl_sock = ssl.wrap_socket(bot_sock, certfile=self.certfile)
        try:
            ssl_sock.bind((listen_ip, port))
        except Exception as e:
            msg = 'Cant bind socket to {}:{}'.format(listen_ip, port)
            self.logger.exception(msg)
            raise BotSocketWrapperException(msg, e)
        ssl_sock.listen(CONNECTIONS_IN_QUEUE)
        self._event_loop(ssl_sock)

    def _event_loop(self, ssl_sock):
        while True:
            try:
                connection, address = ssl_sock.accept()  # address = (IP, PORT)
            except ssl.SSLError as e:
                self.logger.exception(str(e))
                continue
            if address[0] in self.allowed_hosts or '*' in self.allowed_hosts:
                self._event_handler(connection, address[0])
            else:
                msg = 'Blocked IP %s\tServer has allowed IP set to %s' % (
                    address[0], self.allowed_hosts)
                self.logger.warn(msg)
            connection.close()

    def _event_handler(self, connection, ip_address):
        request = recv_by_chunks(connection)
        received_data = pickle.loads(request)
        data_info = get_data_info(received_data)
        msg = "Received data(%s). From IP %s" % (data_info, ip_address)
        self.logger.info(msg)
        try:
            result = self.callback(received_data)
        except Exception as e:
            error = str(e)
            send_by_chunks(connection, pickle.dumps(error))
            msg = "Sent error [ %s ] in response of received data(%s)" % (
                error, data_info)
            self.logger.error(msg)
        else:
            if result is None:
                result = 'None'
            response = pickle.dumps(result)
            send_by_chunks(connection, response)
            data_info = get_data_info(result)
            msg = "Sent data(%s)." % (data_info)
            self.logger.info(msg)
