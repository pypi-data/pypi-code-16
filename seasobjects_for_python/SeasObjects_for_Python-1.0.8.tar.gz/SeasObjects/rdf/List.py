"""
A compatibility class that emulates an RDF List
"""
import sys
try:
    from rdflib import Graph
    from rdflib import BNode
except:
    print "RDFLib is missing from your Python installation"
    print "Install it with"
    print ">  pip install rdflib"
    sys.exit()


class List(object):

    def __init__(self):
        self.elements = []
        
    def parse(self):
        pass
    
    def add_items(self, items):
        if isinstance(items, list):
            self.elements.extend(items)
        else:
            self.elements.append(items)
    
    def get_items(self):
        return self.elements