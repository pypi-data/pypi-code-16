from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.model.PriceSpecification import PriceSpecification

class UnitPriceSpecification(PriceSpecification):
    '''
    classdocs
    '''


    def __init__(self, uri = None):
        '''
        Constructor
        '''
        super(UnitPriceSpecification, self).__init__(uri)
        self.setType(RESOURCE.UNITPRICESPECIFICATION)
        