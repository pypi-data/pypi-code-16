from py2neo import Graph, authenticate
from nameko.extensions import DependencyProvider


class GraphSession(DependencyProvider):

    def setup(self):
        self.db_username = self.container.config['DATABASE']['USERNAME']
        self.db_password = self.container.config['DATABASE']['PASSWORD']
        self.db_url = self.container.config['DATABASE']['URL']
        self.db_endpoint = self.container.config['DATABASE']['ENDPOINT']

    def get_dependency(self):
        authenticate(self.db_url, self.db_username, self.db_password)
        self.graph = Graph(self.db_endpoint)
