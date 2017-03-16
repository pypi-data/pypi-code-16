import atexit
import easyargs
import re

from cassandra.cluster import Cluster
from cassandra.query import tuple_factory

class Cassandra:
    def __init__(self, host, port, keyspace, table):
        self.host = host
        self.port = port
        self.keyspace = keyspace
        self.table = table
        self.cluster, self.session = self.connect()

    def connect(self):
        print('connect to {}:{}'.format(self.host, self.port))
        cluster = Cluster([self.host], port=self.port)
        print('create session for keyspace {}'.format(self.keyspace))
        session = cluster.connect()
        session.row_factory = tuple_factory

        @atexit.register
        def close():
            print('shutdown {}:{}'.format(self.host, self.port))
            cluster.shutdown()
            session.shutdown()

        return cluster, session

    def make_keyspace(self, strategy='SimpleStrategy', replication_factor=1):
        cql = """CREATE KEYSPACE IF NOT EXISTS {}
            WITH replication = {{
                'class': '{}',
                'replication_factor': '{}'
            }}""".format(self.keyspace, strategy, replication_factor)
        print("MAKE KEYSPACE CQL=", cql)
        self.session.execute(cql)


def copy_table_structure(src, dst):
        cql = src.cluster.metadata.keyspaces[src.keyspace].tables[src.table].as_cql_query()
        src_table = src.keyspace + '.' + src.table
        dst_table = 'IF NOT EXISTS ' + dst.keyspace + '.' + dst.table
        cql = cql.replace(src_table, dst_table)
        print("COPY TABLE CQL=", cql)
        dst.session.execute(cql)

def copy_table_data(src, dst, cond):
    cql_select = 'SELECT * FROM {}.{} WHERE {}'.format(src.keyspace, src.table, cond)
    rows = src.session.execute(cql_select)

    stmt = _prepare_insert(src, dst)
    count = 0
    for row in rows:
        dst.session.execute(stmt, row)
        count += 1
    print('INSERT {} rows'.format(count))

def _prepare_insert(src, dst):
    columns = src.cluster.metadata.keyspaces[src.keyspace].tables[src.table].columns.keys()
    value_placeholder = ', '.join(['?'] * len(columns))
    cql_insert = "INSERT INTO {}.{} ({}) VALUES({})".format(dst.keyspace, dst.table, ', '.join(columns), value_placeholder)
    return dst.session.prepare(cql_insert)

def parse(url):
    """
    return host, port, keyspace, table
    """
    host, port, keyspace, table = re.split(':|/', url)
    return host, int(port), keyspace, table

