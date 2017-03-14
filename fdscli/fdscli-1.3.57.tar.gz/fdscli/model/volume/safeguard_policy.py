# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#

from fdscli.model.volume.recurrence_rule import RecurrenceRule
from fdscli.model.base_model import BaseModel

class SafeGuardPolicy(BaseModel):
    '''Named recurrence for use with a SafeGuard subscription.

    Attributes
    ----------
    :type __preset_id: int
    :type __recurrence_rule: ``model.volume.RecurrenceRule``
    '''
    def __init__(self, an_id=-1, name=None, preset_id=None, recurrence_rule=None):
        BaseModel.__init__(self, an_id, name)
        self.recurrence_rule = recurrence_rule
        if self.recurrence_rule is None:
            self.recurrence_rule = RecurrenceRule()
        self.preset_id = preset_id
    
    @property
    def recurrence_rule(self):
        return self.__recurrence_rule
    
    @recurrence_rule.setter
    def recurrence_rule(self, rule):
        self.__recurrence_rule = rule
        
    @property
    def preset_id(self):
        return self.__preset_id
    
    @preset_id.setter
    def preset_id(self, preset_id):
        self.__preset_id = preset_id
