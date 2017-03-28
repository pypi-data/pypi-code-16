import networkx as nx
import pyproteinsExt.uniprot




'''
A Library to store protein protein interaction and homology relationship

Vertices = { A1, {A1'_1, ..., A1'_n}, ... , Am, {Am'_1, ..., Am'_n}}
EdgeTypes = { HomologyRelationship, Interaction }


implement psicquic interface

'''


class Network(nx.Graph):
    super(Network, self).__init__()

    def hExpand(self,nodeList=None):


    def setPsicquic(self):
        pass

    def cureAlias(self):# fuse nodes w/ similar aliases RETURNS A NEW GRAPH
        pass
    def cureHomol(self):# fuse nodes connected by homology relationship
        pass

class addNodes(data):
    if iter(data):
        self.add_nodes(data)
    else:
        self.add_node(data)

class HomologyEdge(object):
    pass

class InteractionEdge(object):
    pass


class Node(object):
    self.entity = None #bounds the object like a uniprot Entry
    self.alias = None #list of string or object



