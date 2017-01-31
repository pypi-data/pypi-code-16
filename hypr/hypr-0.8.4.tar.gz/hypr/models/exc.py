# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Model exceptions."""


class BaseModelException(Exception):
    """Model-related exceptions inherit from this base class."""

    def __init__(self, msg=None):
        """Initialization."""
        super().__init__()
        self._msg = msg

    @property
    def msg(self):  # pragma: no cover
        """The exception message."""
        return self._msg

    def __str__(self):  # pragma: no cover
        """__str__"""
        return self.msg


class ModelInvalidOperation(BaseModelException):
    """The operation is not possible"""


class ModelConflictException(ModelInvalidOperation):
    """A model instance is conflicting with another model instance."""


class ModelConsistencyException(BaseModelException):
    """The database state is not consistent due to a pending transaction."""
