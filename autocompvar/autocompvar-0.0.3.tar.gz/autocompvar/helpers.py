#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
try:
    from .metadata import gen_code
    from .name_convention import to_variable_name
except:
    from autocompvar.metadata import gen_code
    from autocompvar.name_convention import to_variable_name
    
def create_data_script(metadata):
    """Create an importable python script stands for the object orientied style
    data visiting.
    
    Warning! This will silently overwrite files. Use this function when you
    fully understand what it does.
    """
    code = gen_code(metadata)
    filename = "%s.py" % to_variable_name(metadata["classname"])
    with open(filename, "wb") as f:
        f.write(code.encode("utf-8"))