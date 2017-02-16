'''
Created on Jan 26, 2017

@author: nate
'''
class ContextDef(object):
    '''
    A context definition for a stats query.  The statics here are valid types
    '''

    VOLUME = "VOLUME"
    NODE = "NODE"
    DOMAIN = "DOMAIN"

    def __init__(self, context_type=None, context_id=-1):
        '''
        Constructor
        '''
        
        self.context_type = context_type
        self.context_id = context_id
        
    @property
    def context_type(self):
        return self.__context_type
    
    @context_type.setter
    def context_type(self, a_type):
        self.__context_type = a_type
        
    @property
    def context_id(self):
        return self.__context_id
    
    @context_id.setter
    def context_id(self, an_id):
        self.__context_id = an_id
        