#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysharkpatch.py

Patch the ``pyshark`` class ``LayerFieldsContainer`` using
inheritance to override its ``__new__`` method so that it
is pickleable.

"""
from pyshark.packet import layer
class LayerFieldsContainer(layer.LayerFieldsContainer):
    def __new__(cls, main_field, *args, **kwargs):
        if hasattr(main_field, 'get_default_value'):
            obj = str.__new__(cls, main_field.get_default_value(), *args, **kwargs)
        else:
            obj = str.__new__(cls, main_field, *args, **kwargs)
        obj.fields = [main_field]
        return obj
layer.LayerFieldsContainer = LayerFieldsContainer
