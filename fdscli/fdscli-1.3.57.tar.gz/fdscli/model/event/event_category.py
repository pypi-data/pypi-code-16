# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#

from enum import Enum, unique

@unique
class EventCategory(Enum):
    '''
    Standard event categories.  An event may be associated with 
    multiple categories, such as VOLUME and PERFORMANCE.  At the event level
    they are simple string and are not strictly limited to the enumerated values.
    '''
    user        = 0
    firebreak   = 1
    volumes     = 2
    storage     = 3
    system      = 4
    performance = 5
    node        = 6
    service     = 7

    def __str__(self):
        if self.value == EventCategory.user.value:
            return 'USER'
        if self.value == EventCategory.firebreak.value:
            return 'FIREBREAK'
        if self.value == EventCategory.volumes.value:
            return 'VOLUMES'
        if self.value == EventCategory.storage.value:
            return 'STORAGE'
        if self.value == EventCategory.system.value:
            return 'SYSTEM'
        if self.value == EventCategory.performance.value:
            return 'PERFORMANCE'
        if self.value == EventCategory.node.value:
            return 'NODE'
        if self.value == EventCategory.service.value:
            return 'SERVICE'
        return self.name

