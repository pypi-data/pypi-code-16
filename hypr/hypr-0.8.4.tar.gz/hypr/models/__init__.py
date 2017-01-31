# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Available models."""


import sys
import pkg_resources as pkg_resources
from hypr.models.sqlite import SQLiteModel


available_models = ['SQLiteModel']

for ep in pkg_resources.iter_entry_points('hypr.models'):
    model = ep.load()
    setattr(sys.modules[__name__], model.__name__, model)
    available_models.append(model.__name__)


__all__ = tuple(available_models)
