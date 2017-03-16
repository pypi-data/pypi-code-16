import sys

from cassandra import policies
from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.policies import DCAwareRoundRobinPolicy
from cherrypy.process import plugins


class CassandraClient(plugins.SimplePlugin):
    def __init__(self, config):
        self.keyspace = config.cassandra.keyspace
        self.cluster = Cluster(
                contact_points=config.cassandra.contact_points,
                port=config.cassandra.port,
                load_balancing_policy=policies.TokenAwarePolicy(policies.DCAwareRoundRobinPolicy(local_dc=config.cassandra.datacenter)),
                executor_threads=10,
                connect_timeout=2,
                control_connection_timeout=2,
                compression='lz4',
                max_schema_agreement_wait=0
        )
        self.session = None

    def connect(self):
        if self.session and not self.session.is_shutdown:
            print("CassandraClient: already connected")

        try:
            self.session = self.cluster.connect(keyspace=self.keyspace)
        except NoHostAvailable:
            print(
                    "CassandraClient: Error....couldn't connect to Cassandra."
                    "Check firewall settings for the cluster or your connection."
            )
            sys.exit(1)

    def disconnect(self):
        self.cluster.shutdown()

    def stop(self):
        self.disconnect()
        self.exit = True

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()
