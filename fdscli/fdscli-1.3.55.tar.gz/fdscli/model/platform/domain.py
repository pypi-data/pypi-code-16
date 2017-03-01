from fdscli.model.base_model import BaseModel

class Domain(BaseModel):
    '''
    Created on Apr 28, 2015
    
    @author: nate
    '''
    STATE_DOWN = "DOWN"
    STATE_UP = "UP"
    STATE_UNKNOWN = "UNKNOWN"

    def __init__(self, an_id=-1, name=None, site="local", state=STATE_UNKNOWN):
        BaseModel.__init__(self, an_id, name)
        self.site = site
        self.state=state
        
    @property
    def site(self):
        return self.__site
    
    @site.setter
    def site(self, site):
        self.__site = site
        
    @property
    def state(self):
        return self.__state
    
    @state.setter
    def state(self, state):
        if ( state not in (Domain.STATE_UP, Domain.STATE_DOWN, Domain.STATE_UNKNOWN) ):
            raise TypeError()
            return
        self.__state = state
