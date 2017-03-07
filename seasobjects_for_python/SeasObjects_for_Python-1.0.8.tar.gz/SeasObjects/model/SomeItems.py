from SeasObjects.model.GrObj import GrObj
from SeasObjects.model.SystemOfInterest import SystemOfInterest
from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
import traceback

class SomeItems(GrObj):
    '''
    classdocs
    '''


    def __init__(self, uri = None, type=None, name=None, description=None, systemOfInterestSameAs=None):
        super(SomeItems, self).__init__(uri)
        self.setType(RESOURCE.SOMEITEMS)
        if type is not None:
            self.addType(type)
        if name is not None:
            self.setName(name)
        if description is not None:
            self.setDescription(description)
        
        self.systemOfInterest = None
        if systemOfInterestSameAs is not None:
            self.setSystemOfInterestWithSameAs(systemOfInterestSameAs)       
        
    def hasSystemOfInterest(self):
        return self.systemOfInterest is not None
    
    def getSystemOfInterest(self):
        return self.systemOfInterest
    
    def setSystemOfInterest(self, system):
        self.systemOfInterest = system
        
    def setSystemOfInterestWithSameAs(self, sameAs):
        soi = SystemOfInterest()
        soi.setSameAs(sameAs)
        self.setSystemOfInterest(soi)
        
    def setSystemOfInterestWithType(self, *types):
        soi = SystemOfInterest()
        soi.clearTypes()
        for t in types:
            soi.addType(t)
            
        self.setSystemOfInterest(soi)
        
    def serialize(self, model):        
        '''
        return a rdf resource
        '''
        if self.serializeAsReference:
            return self.serializeToReference(model)
        
        resource = super(SomeItems, self).serialize(model)
        if self.hasSystemOfInterest():
            resource.addProperty(model.createProperty(PROPERTY.SYSTEMOFINTEREST), self.systemOfInterest.serialize(model) )
        
        return resource
        
    def parseStatement(self, statement):
        # get predicate
        predicate = str(statement.getPredicate())
        if predicate == PROPERTY.SYSTEMOFINTEREST:
            try:
                self.setSystemOfInterest(SystemOfInterest.parse(statement.getResource()))
            except:
                print "Unable to interpret seas:systemOfInterest value as resource."
                traceback.print_exc()
            return
        
        super(SomeItems, self).parseStatement(statement)    
                  
        