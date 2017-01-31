#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

from .vararray import EUDVArray
from ...utils import ExprProxy


class _EUDStruct_Metaclass(type):
    def __mul__(self, times):
        basetype = self

        class EUDStructArray(ExprProxy):
            __metaclass__ = _EUDStruct_Metaclass

            def __init__(self, initvar=None):
                if initvar is None:
                    initvals = [basetype() for _ in range(times)]
                    super().__init__(EUDVArray(times, basetype)(initvals))
                else:
                    super().__init__(EUDVArray(times, basetype)(initvar))

                self._initialized = True
                self.dontFlatten = True

            def clone(self):
                """ Create struct clone """
                arraytype = type(self)
                inst = arraytype()
                self.deepcopy(inst)
                return inst

            def deepcopy(self, inst):
                """ Copy struct to other instance """
                for i in range(times):
                    self[i].deepcopy(inst[i])

            def __getitem__(self, index):
                return self.getValue()[index]

            def __setitem__(self, index, newval):
                self.getValue()[index] = newval

            def __getattr__(self, name):
                return super().__getattr__(name)

            def __setattr__(self, name, value):
                self.__dict__[name] = value

        return EUDStructArray
