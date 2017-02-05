import collections

import grpc

from pygraphflow import q # query
from pygraphflow import g # graph
from pygraphflow import datatype
from pygraphflow.rpc import GraphflowServer_pb2

class GraphFlowClient():
    def __init__(self, url = 'localhost', port = '8080'):
        self.channel = grpc.insecure_channel(url + ':' + str(port))
        self.stub = GraphflowServer_pb2.GraphflowServerQueryStub(self.channel)

    def execute_query(self, query):
        response = self.stub.ExecuteQuery(GraphflowServer_pb2.
                                          ServerQueryString(message=query))
        return response

    def match(self, edges):
        self.execute_query(self.get_query(edges, q.MATCH))

    def continuous_match(self, edges, Udf):
        self.execute_query(self.get_query(edges, q.CONTINUOUS_MATCH) + str(Udf))

    def create(self, edges_and_vertices):
        self.execute_query(self.get_query(edges_and_vertices, q.CREATE))

    def delete(self, edge):
        self.execute_query(self.get_query(edge, q.DELETE))

    def set(self, id_properties_map):
        pass

    def get_query(self, edges_and_vertices, query):
        for index, e_or_v in enumerate(edges_and_vertices):
            if index > 0:
                query += ', '
            query += str(e_or_v)
        return query
