from SeasObjects.model.Obj import Obj
from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE

class GrObj(Obj):
    '''
    classdocs
    '''

    def __init__(self, uri = None):        
        super(GrObj, self).__init__(uri)
        self.grName = None
        self.grDescription = None
    
    def hasGrName(self):  
        return self.grName is not None
    
    def setGrName(self, gname):
        self.grName = gname
        
    def getGrName(self):
        return self.grName  
    
    def hasGrDescription(self):
        return self.grDescription is not None
    
    def getGrDescription(self):
        return self.grDescription
    
    def setGrDescription(self, gdescription):
        self.grDescription = gdescription
        
    def serialize(self, model):
        '''
        return a rdf.Resource
        '''
        if self.serializeAsReference:
            return self.serializeToReference(model)
        
        resource = super(GrObj, self).serialize(model)
        if self.hasGrName():
            resource.addProperty(model.createProperty( PROPERTY.NAME), self.grName)  
        if self.hasGrDescription():
            resource.addProperty(model.createProperty( PROPERTY.GR_DESCRIPTION), self.grDescription)      
        
        return resource
    
    def parseStatement(self, statement):
        
        # get predicate
        predicate = str(statement.getPredicate())
        
        if predicate==PROPERTY.NAME:
            self.setGrName(statement.getString())
            return
        
        if predicate == PROPERTY.GR_DESCRIPTION:
            self.setGrDescription(statement.getString())
            return
        
        super(GrObj, self).parseStatement(statement)
    