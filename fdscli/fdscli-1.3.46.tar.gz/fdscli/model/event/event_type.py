# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#

from enum import Enum, unique

@unique
class EventType(Enum):
    user_activity   = 0
    system_event    = 1
    firebreak_event = 2

    def __str__(self):
        if self.value == EventType.user_activity.value:
            return "USER_ACTIVITY"
        if self.value == EventType.system_event.value:
            return "SYSTEM_EVENT"
        if self.value == EventType.firebreak_event.value:
            return "FIREBREAK_EVENT"
        return self.name

