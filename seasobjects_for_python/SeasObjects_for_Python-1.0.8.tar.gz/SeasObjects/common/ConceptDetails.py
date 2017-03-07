from rdflib import Graph, URIRef, RDF
import rdflib

class ConceptDetails(object):
    '''
    used by Obj.explain() method. It fetches concept detail from seas Ontology files
    
    TODO
    '''
    
    def __init__(self):
        import tempfile               
        # create temporary folder for keeping persistent graph store.
        self.tmpdir = tempfile.mkdtemp()
        
        self.ontStore = self.loadOntologies()

     
    def getComments(self, resourceUri):  
        '''
        @param resourceUri: URI string of the resource
        @return rdfs:label and rdfs:comments value of this Resource as a String
        '''
        label = self.ontStore.label(URIRef(resourceUri))
        comment = self.ontStore.comment(URIRef(resourceUri))
                
        return '%s  (%s)' % (label, comment) 
    
    
    def loadOntologies(self):
               
        print '----initalize conceptDetailsEngine-----'
        # See: http://rdflib.readthedocs.io/en/stable/persistence.html
        seas = Graph(store='Sleepycat', identifier='seasGraph')
        seas.open(self.tmpdir, create = True)
        seas.parse(source='http://seas.asema.com/seas-1.0_joined.ttl', format='turtle')
        #seas.
        
        quantity = Graph()
        quantity.parse('http://www.qudt.org/qudt/owl/1.0.0/quantity.owl', format='xml' )        
        seas = seas + quantity
        unit = Graph()
        unit.parse('http://www.qudt.org/qudt/owl/1.0.0/unit.owl', format = 'xml')
        seas = seas + unit
        
        #print("seas ontology has %s statements." % len(seas))
        
        return seas
    
    def close(self):
        '''
        free opened resources/clean up
        '''
        import shutil
        
        self.ontStore.close()
        shutil.rmtree(self.tmpdir)
        

    