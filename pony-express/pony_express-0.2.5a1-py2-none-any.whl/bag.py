import collections
import json
from config_constrainer import config_generator, ConfigurationImpossible
from  pymongo import MongoClient
import dependencies as dep
import networkx as nx

import sys
from bson.binary import Binary


class ImpossibleConfigurationException(Exception):
    """Exception raised in case pony can't find an acceptable dependency configuration."""
    def __init__(self, gr):
        self.gr = gr

    def __str__ (self):
        return """Can't fulfill all dependencies in a compatible way.
The dependency graph is
""" + to_dot_string(self.gr)


def no_dependencies():
    return [], nx.DiGraph()

def quote(s, qm = '"'):
    return qm+ str(s) + qm

def to_dot_string(G):
    """
    Construct a string that represent the graph using dot languale.
    It assumes G is a directed graph.
    """

    dot_string = "digraph {\n"
    # first print out any node to be sure to not forget any isolated node
    sorted_nodes = G.nodes()
    sorted_nodes.sort()
    for n in sorted_nodes:
        n_dep = ''
        try:
            n_dep = G.node[n]['ndep']
        except:
            pass

        #dot_string += "    " + quote( str(n) +  '( ndep: ' + str(n_dep)+ ')') + " [penwidth=3 "
        dot_string += "    " + quote( str(n)) + " [penwidth=3 "
        if('invalid' in G.node[n]):
            dot_string += "color=red "
        elif G.node[n]['pruned']:
            dot_string += "color=blue "
        dot_string += "];\n"

    dot_string += "\n"

    # then write down any edge
    sorted_edges = G.edges(data=True)
    sorted_edges.sort()
    for edge in sorted_edges:
        dot_string += "    " +  quote(edge[0]) + " -> " + quote(edge[1]) 
        if 'valid' in edge[2]:
            if edge[2]['valid']:
                dot_string += '[color=black penwidth=3]'
            else:
                dot_string += '[color=red penwidth=3]'

        dot_string += ";\n"
    dot_string += "}\n"

    return dot_string


class MongoConnectionInfo:
    def __init__(self, pony_arguments = None):
        if pony_arguments and pony_arguments.user:
            self.host = pony_arguments.mongo
            self.port = pony_arguments.port
            self.user = pony_arguments.user
            self.pwd = pony_arguments.pwd
            self.controlled_access  = True
        else:
            self.host = 'localhost'
            self.port = 27017
            self.controlled_access  = False
            
            
    def connect(self):
        cli= MongoClient(host = self.host, port=self.port)
        print('connecting to: ' + self.host + ' : ' + str(self.port) + ' [controlled:' + str(self.controlled_access) + ']' )
        if self.controlled_access:
            cli.pony_store.authenticate(self.user, self.pwd)
        return cli

class YetInBag (Exception):
    
    def __init__ (self, meta_informations):
        self.explain = meta_informations
        
    def __str__ (self):
        return """
        Error trying to insert package into the bag. 
                It contains yet a package with same metadata. Perhaps you want to increase your version.
        
        Received metadata:
          """ + self.explain 
        
    def __str__ (self):
        return """
        Error trying to insert package into the bag. 
                It contains yet a package with same metadata. Perhaps you want to increase your version.
        
        Received metadata:
          """ + str(self.explain) 

class NotInBag (Exception):

    def __init__ (self, meta_informations):
        self.explain = meta_informations
        
    def __str__ (self):
        return """
        Error trying to take package from the bag. 
                It do not contains yet a package with compatible metadata.
        
        Received metadata:
          """ + str(self.explain) 

class Bag:
    def __init__(self, db_connection_info=MongoConnectionInfo()):
        # setup the mongo connection
        self.connection = db_connection_info.connect()
        self.collection = self.connection.pony_store.packages
        self.silent = False

    def encode_requirements(self, meta):
        if "DEPENDENCIES" in meta.keys():
            meta["DEPENDENCIES"] = json.dumps(meta["DEPENDENCIES"])
        return meta

    def decode_requirements(self, meta):
        query_requirements = []
        requirements = []
        if "DEPENDENCIES" in meta.keys():
            query_requirements = json.loads(meta["DEPENDENCIES"])
            for query in query_requirements:
                mongo_cursor = self.collection.find(query)
                for r in mongo_cursor:
                    requirements.append(r)

            meta['DEPENDENCIES'] = requirements
        return requirements

    def check(self, meta):
        same_meta_cursor = self.collection.find(meta)
        fail = same_meta_cursor.count() > 0
        if fail:
            pass#print(same_meta_cursor[0])
        return fail

    def charge (self,  package, meta):
        meta = self.encode_requirements(meta)
        if(self.check(meta)):
            raise YetInBag(meta)
        # add content to metadata. it will become a rich package!
        if sys.version_info < (3, 0):
            meta['package'] = Binary(package)
        else:
            meta['package'] = package
        id = self.collection.insert_one(meta)
        
        del meta['package']
        if not self.silent:
            print ('package archived')
            print (str(meta))
    
    def _select_all(self, meta_request):
        """Select all alternative package matching the request"""

        if type(meta_request) is dep.Requirement:
            meta_request = meta_request.meta_request()

        matching_packages = self.collection.find(meta_request)
        if matching_packages.count() == 0:
            raise NotInBag(meta_request)
        
        # return the first matching package
        return matching_packages
            
    def _select(self,meta_request):
        """Select an arbitrary alternative requested package from the set of matching one"""
        selection = []
        matching_packages = self._select_all(meta_request)
        
        
        for p in matching_packages:
            selection.append(p)
        
        for p in selection:
            p = self.decode_requirements(p)
                
        # return the first matching package
        return selection[0] 
        
    
    def take(self, meta_request):
        # take the package from charged document
        package = self._select(meta_request)['package']
        return package
        
    def translate_requirements(self, requests, select_any = True):
        """Translates the requirements into an explicit requirement given the matching boxed into actually in the bag. """
        
        if not isinstance(requests, list):
            requests = [requests]    

        meta_requests = [r.meta_request() for r in requests]

        requirements =[]
        for meta_request in meta_requests:
            for p in self._select_all(meta_request):
                requirements.append(dep.Requirement(p))
            
        return requirements



    def requirements_for (self, request, select_any = True):
        """
        Retrieve additional dependencies for a requirements_for
        """
        dependant_projects = set()
        meta_request = request.meta_request()
        package = self._select(meta_request) if select_any else self._select_all(meta_request)
        requirements = []
        try:
            requirements = dep.make_direct(package['DEPENDENCIES'], parent=request)
        except KeyError:
            # no dependencies for this package!
            pass
            
        return requirements
      
    def requirements_graph (self, direct_requirements, known_nodes = []):
        gr = nx.DiGraph()

        if not isinstance(direct_requirements, collections.Iterable):
            direct_requirements = [direct_requirements]

        while len(direct_requirements) > 0:
            req = direct_requirements.pop()
            more_requirements = self.requirements_for(req)
            #more_requirements.remove(req)

            local_gr = nx.DiGraph()
            for child_req in more_requirements:
                gr.add_edge(req, child_req, valid=True)
                gr.node[child_req]['pruned'] = False

            gr.add_node(req)
            gr.node[req]['pruned'] = False
            _gr = to_dot_string(gr)
            
            # get the graph describing the direct requirements requirements
            # then join it with the one describing direct requirements (local)
            sub_gr = self.requirements_graph(more_requirements)
            
            gr = nx.compose(gr, sub_gr)
            
        return gr
    
    def acceptable_configurations(self, gr):
        if len(gr.nodes()) == 0:
            return [gr]
        
        acceptable_config_generator = config_generator(gr)
        try:
            configurations = [config for config in acceptable_config_generator.constraint() ]
        except ConfigurationImpossible:
            raise ImpossibleConfigurationException(gr)

        return configurations

    def first_acceptable_configuration(self, gr):
        if len(gr.nodes()) == 0:
            return [gr]
        
        acceptable_config_generator = config_generator(gr)
        try:
            config = next(acceptable_config_generator.constraint())
        except ConfigurationImpossible:
            raise ImpossibleConfigurationException(gr)

        return config

    def requirements_discover(self, direct_requirements):
        direct_requirements = self.translate_requirements(direct_requirements, select_any=False)
        raw_graph = self.requirements_graph(direct_requirements)

        graph = self.first_acceptable_configuration(raw_graph)
      
        return [n for n in graph.nodes() if not graph.node[n]['pruned']], graph