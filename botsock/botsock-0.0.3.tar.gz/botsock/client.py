import pickle
import socket
import ssl

from .settings import PORT, SERVER_IP
from .utils import get_data_info, get_logger, recv_by_chunks


def send_data(data,
              server_ip=SERVER_IP,
              port=PORT,
              certfile='cert.pem',
              logfile='logging.yml'):
    logger = get_logger(__name__, logfile)
    sock = socket.socket()
    sock.connect((server_ip, port))
    ssl_sock = ssl.wrap_socket(sock, certfile=certfile)
    request = pickle.dumps(data)
    ssl_sock.send(request)
    msg = "Sent data(%s)" % (data.__class__.__name__)
    logger.info(msg)
    response = recv_by_chunks(ssl_sock)
    data = pickle.loads(response) if response else 'None'
    data_info = get_data_info(data)
    msg = "Received data(%s)" % data_info
    logger.info(msg)
    sock.close()
    return data
