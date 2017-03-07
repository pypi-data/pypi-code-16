from SeasObjects.model.GrObj import GrObj
from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
from rdflib import XSD
from SeasObjects.rdf.Variant import Variant
import traceback

class PriceSpecification(GrObj):
    '''
    classdocs
    '''


    def __init__(self, uri = None):
        super(PriceSpecification, self).__init__(uri)
        #String 
        self.currency = None
        #Float 
        self.currencyValue = None
        #Date 
        self.validThrough =  None
        # Boolean 
        self.valueAddedTaxIncluded = None
        # Variant 
        self.vatPercentage = None
    
    def hasCurrency(self):
        return self.currency is not None    
    def getCurrency(self):
        return self.currency
    def setCurrency(self, cur):
        self.currency = cur
    
    def hasCurrencyValue(self):
        return self.currencyValue is not None    
    def getCurrencyValue(self):
        return self.currencyValue    
    def setCurrencyValue(self, cv):
        self.currencyValue = cv
        
    def hasValidThrough(self):
        return self.validThrough is not None
    def getValidThrough(self):
        return self.validThrough
    def setValidThrough(self, vt):
        self.validThrough = vt
    
    def hasValueAddedTaxIncluded(self):
        return self.valueAddedTaxIncluded is not None
    def getValueAddedTaxIncluded(self):
        return self.valueAddedTaxIncluded
    def setValueAddedTaxIncluded(self, vat):
        self.valueAddedTaxIncluded = vat
    
    def hasVatPercentage(self):  
        return self.vatPercentage is not None
    def getVatPercentage(self): 
        return self.vatPercentage
    def setVatPercentage(self, vp):  
        self.vatPercentage = vp
    
    def serialize(self, model):
        if self.serializeAsReference:
            return self.serializeToReference(model)
        
        resource = super(PriceSpecification, self).serialize(model)
        #currency
        if self.hasCurrency():
            resource.addProperty(model.createProperty( PROPERTY.HASCURRENCY ), model.createLiteral(self.currency))
        #currencyValue
        if self.hasCurrencyValue():
            resource.addProperty(model.createProperty( PROPERTY.HASCURRENCYVALUE ), model.createTypedLiteral(self.getCurrencyValue(), XSD.float))
        #validThrough
        if self.hasValidThrough():
            resource.addProperty(model.createProperty( PROPERTY.VALIDTHROUGH), model.createLiteral(self.getValidThrough()))
        # valueAddedTaxIncluded
        if self.hasValueAddedTaxIncluded():
            resource.addProperty(model.createProperty( PROPERTY.VALUEADDEDTAXINCLUDED),
                                 model.createTypedLiteral(self.getValueAddedTaxIncluded(), XSD.boolean ))    
        # vatPercentage
        if self.hasVatPercentage():
            resource.addProperty(model.createProperty(PROPERTY.VATPERCENTAGE), self.vatPercentage.serialize(model))
        
        return resource   
    
    def parseStatement(self, statement):
        
        # get predicate
        predicate = str(statement.getPredicate())
        
        if predicate == PROPERTY.HASCURRENCY:
            try:
                self.setCurrency(statement.getString())    
            except:
                print "Unable to interpret gr:hasCurrency value as literal string."
                traceback.print_exc()
            return  
        
        if predicate == PROPERTY.HASCURRENCYVALUE: 
            try:
                self.setCurrencyValue(statement.getFloat())
            except:
                print "Unable to interpret gr:hasCurrencyValue value as literal float."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.VALIDTHROUGH:
            try:
                self.setValidThrough(statement.getObject().toPython())                
            except:                
                print "Unable to interpret gr:validThrough value as date literal."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.VALUEADDEDTAXINCLUDED:
            try:
                self.setValueAddedTaxIncluded(statement.getBoolean())
            except:
                print "Unable to interpret gr:valueAddedTaxIncluded value as literal boolean."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.VATPERCENTAGE:            
            self.setVatPercentage(Variant().parse(statement))
            return
        
        super(PriceSpecification, self).parseStatement(statement)  