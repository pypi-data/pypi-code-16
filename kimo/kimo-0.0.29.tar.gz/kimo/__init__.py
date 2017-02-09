import logging
import threading
import Queue
from collections import OrderedDict

import mysql.connector
import requests
from requests.exceptions import ConnectionError

from kimo import conf

logger = logging.getLogger()


def get_mysql_processlist(db_conf):
    """
    Get the list of MySQL processes.
    """
    # Connect to the database
    connection = mysql.connector.connect(host=db_conf['host'],
                                         user=db_conf['user'],
                                         password=db_conf['password'],
                                         db='information_schema')

    try:
        cursor = connection.cursor()
        # Create a new record
        cursor.execute(
                'SELECT ID, User, host, db, Command, Time, State, Info FROM PROCESSLIST')
        rows = []
        while True:
            row = cursor.fetchone()
            if not row:
                break

            # OrderedDict is used because, we want to use columnd nanmes in the same order with the query.
            rows.append(OrderedDict(zip(cursor.column_names, row)))

        logger.debug('Return %s rows.', len(rows))
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

    finally:
        connection.close()

    return rows


def get_pid(host_addr, port_number, proxy_host=None):
    """
    Get the process id of the MySQL query.
    """
    source_host = 'http://' + host_addr + ':' + str(conf.KIMO_SERVER_PORT) + '/connections'
    try:
        session = requests.Session()
        response = session.get(source_host, timeout=(30, 60))
    except ConnectionError as e:
        logger.error('Could not connect to kimo server on host: %s', host_addr)
        logging.error(e, exc_info=True)
        return 'Error', 'Error'

    try:
        response.raise_for_status()
    except Exception as e:
        logger.error('Error when connecting to kimo server on host: %s', host_addr)
        logging.error(e, exc_info=True)
        return 'Error', 'Error'

    connections = response.json()

    for conn in connections:
        if host_addr in conn['laddr'][0] and port_number == conn['laddr'][1]:
            break
    else:
        logger.debug('Could not found a connection for host: %s port: %s', host_addr, port_number)
        return 'Error', 'Error'

    if conn['process']['name'] == 'tcpproxy':
        if not proxy_host:
            logger.error('Proxy Host must be provided!')
            return 'Error-Tcp', 'Error-Tcp'
        logger.debug('Found tcpproxy! Getting connections from tcpproxy: %s', proxy_host)
        try:
            response = session.get(proxy_host, timeout=(30, 60))
        except ConnectionError as e:
            logger.error('Could not connect to tcpproxy: %s', proxy_host)
            logging.error(e, exc_info=True)
            return 'Error', 'Error'

        try:
            response.raise_for_status()
        except Exception as e:
            logger.error('Error when connecting tcpproxy server: %s', proxy_host)
            logging.error(e, exc_info=True)
            return 'Error', 'Error'

        # Sample Output:
        # 10.0.4.219:36149 -> 10.0.0.68:3306 -> 10.0.0.68:35423 -> 10.0.0.241:3306
        # <client>:<output_port> -> <proxy>:<input_port> -> <proxy>:<output_port>: -> <mysql>:<input_port>
        connection_lines = response.content.split('\n')
        for conn in connection_lines:
            line = conn.replace(' ', '').split('->')
            if len(line) < 3:
                continue

            host, port = line[2].split(':')
            port = int(port)
            if host == host_addr and port == port_number:
                break
        else:
            return None, None

        line = conn.replace(' ', '').split('->')
        host, port = line[0].split(':')
        port = int(port)
        return get_pid(host, port, proxy_host=proxy_host)

    return host_addr, conn['process']


def get_pids(db_conf, proxy_host=None, query_id=None):
    """
    Get process ids of MySQL queries.
    """
    db_process_list = get_mysql_processlist(db_conf)
    db_process_list = filter(lambda x: x['host'] != 'localhost', db_process_list)
    # Look for a specific query id, ignore rest.
    if query_id:
        db_process_list = filter(lambda x: str(x['ID']) == str(query_id), db_process_list)

    def wrapper_get_pid(*args, **kwargs):
        q.put(get_pid(*args, **kwargs))

    q = Queue.Queue()
    threads = []
    for db_process in db_process_list:
        host, port = db_process['host'].split(':')
        port = int(port)
        t = threading.Thread(target=wrapper_get_pid, args=(host, port), kwargs={'proxy_host': proxy_host})
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    results = []
    while not q.empty():
        results.append(q.get())

    combined_result = []
    for idx, result in enumerate(results):
        db_process_dict = db_process_list[idx]

        process_cmdline = None
        process_pid = None
        process_host = None
        if result[1]:
            if 'Error' in result[1]:
                process_cmdline = result[1]
                process_pid = result[1]
            else:
                process_pid = result[1]['pid']
                if result[1].get('cmdline'):
                    process_cmdline = ' '.join(result[1]['cmdline'])
        if result[0]:
            process_host = result[0]

        process_dict = {
                'Process_id': process_pid,
                'Process_host': process_host,
                'Process_cmdline': process_cmdline
        }
        db_process_dict.update(process_dict)

        combined_result.append(db_process_dict)

    return combined_result
