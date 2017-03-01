# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#

from fdscli.model.base_model import BaseModel
from fdscli.model.volume.recurrence_rule import RecurrenceRule

class SafeGuardPreset( BaseModel ):
    '''A prototypical SafeGuard policy.

    Attributes
    ----------
    :type __recurrence_rule: ``model.volume.RecurrenceRule``
    '''
    def __init__(self, recurrence_rule=None, an_id=-1, name=None):
        BaseModel.__init__(self, an_id, name)
        self.recurrence_rule = recurrence_rule
        if self.recurrence_rule is None:
            self.recurrence_rule = RecurrenceRule()

    @property
    def recurrence_rule(self):
        return self.__recurrence_rule

    @recurrence_rule.setter
    def recurrence_rule(self, rule):
        self.__recurrence_rule = rule
