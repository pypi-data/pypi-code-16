# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
from enum import Enum, unique

@unique
class CompletionStatus(Enum):
    unknown   = 0
    initiated = 1  # OM received request
    pending   = 2  # Xdi received request
    blocked   = 3  # CDR-Snap tasks must execute in sequence
    running   = 4  # Data transfer in progress
    done      = 5
    failed    = 6  # Failed with retries remaining
    abandoned = 7  # Failed with no retries remaining
    cancelled = 8  # Cancelled at user request

    def __str__(self):
        if self.value == CompletionStatus.running.value:
            return "in_progress"
        return self.name
