# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#

from enum import Enum, unique

@unique
class EventSeverity(Enum):
    info     = 0
    config   = 1
    warning  = 2
    error    = 4
    critical = 5
    fatal    = 6

    def __str__(self):
        if self.value == EventSeverity.info.value:
            return 'INFO'
        if self.value == EventSeverity.config.value:
            return 'CONFIG'
        if self.value == EventSeverity.warning.value:
            return 'WARNING'
        if self.value == EventSeverity.error.value:
            return 'ERROR'
        if self.value == EventSeverity.critical.value:
            return 'CRITICAL'
        if self.value == EventSeverity.fatal.value:
            return 'FATAL'
        return self.name

