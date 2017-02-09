import sys
import os
import logging
import argparse

from terminaltables import AsciiTable

from kimo import get_pids

logger = logging.getLogger('kimo')
logger.setLevel(logging.INFO)

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def main():

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Find the process ids of a MySQL queries.')

    parser.add_argument('--query_id',
                        dest='query_id',
                        type=str,
                        help='Look for a specific query')
    parser.add_argument('--host',
                        dest='host',
                        type=str,
                        help='Host of database')
    parser.add_argument('--user',
                        dest='user',
                        type=str,
                        help='User for database')
    parser.add_argument('--password',
                        dest='password',
                        type=str,
                        help='Password for database')
    parser.add_argument('--proxy_host',
                        dest='proxy_host',
                        type=str,
                        help='Proxy host address')

    args = parser.parse_args()

    query_id = args.query_id or None
    proxy_host = args.proxy_host or None

    db_conf = {}
    db_conf['host'] = args.host or 'localhost'
    db_conf['user'] = args.user or ''
    db_conf['password'] = args.password or ''

    result = get_pids(db_conf, proxy_host=proxy_host, query_id=query_id)
    print_result(result)


def print_result(result):
    """
    Print the result in a tabular form.
    """
    # The header is in order with the result order.
    table_data = [
            result[0].keys()
    ]

    for r in result:
        table_data.append(r.values())

    table = AsciiTable(table_data)
    print table.table

if __name__ == '__main__':
    main()
