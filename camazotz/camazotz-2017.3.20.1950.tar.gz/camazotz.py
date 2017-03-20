# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# camazotz                                                                     #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program compiles and loads C code in Python code.                       #
#                                                                              #
# copyright (C) 2017 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################
"""

from __future__ import division
import ctypes
import os
import shlex
import sys
import tempfile

name    = "camazotz"
version = "2017-03-20T1950Z"

try:
    executable_compiler = os.environ["CC"]
except KeyError:
    print("CC environment variable must point to C compiler", file = sys.stderr)
    sys.exit(1)

class C:

    """
    This class compiles and loads C code in Python code, optionally linking
    other shared libraries along with loaded code.
    """

    def __init__(
        self,
        code,
        *shared_libraries
        ):

        self.library = None
        self._compile(code, shared_libraries)

    def _compile(
        self,
        code,
        libraries
        ):

        """
        Compile C code to shared library and link it to the working program. All
        shared libraries specified are also linked to the shared library and,
        thus, loaded to the working program also.
        """

        # save C code
        with tempfile.NamedTemporaryFile(
            mode   = "w",
            prefix = "PYC",
            suffix = ".c", 
            delete = False
        ) as file_temporary_c:
            filename_temporary_c = file_temporary_c.name
            file_temporary_c.write(code)
            file_temporary_c.flush()

        # generate object files
        filename_object = tempfile.mktemp(
            prefix = "PYC",
            suffix = ".o"
        )
        print(
            "compile C code {filename_temporary_c} to object file "\
            "{filename_object}".format(
            filename_temporary_c = filename_temporary_c,
            filename_object      = filename_object
        ))
        os.system(
            "{compiler} -c -o {output} {input}".format(
                compiler = executable_compiler, 
                output   = shlex.quote(filename_object), 
                input    = shlex.quote(filename_temporary_c)
            )
        )

        # generate shared library
        filename_shared_object = tempfile.mktemp(
            prefix = "PYC",
            suffix = ".so"
        )
        print("compile library {filename_shared_object}".format(
            filename_shared_object = filename_shared_object
        ))
        os.system(
            "{compiler} -shared -o {output} {input} {libraries}".format(
                compiler  = executable_compiler,
                output    = shlex.quote(filename_shared_object),
                input     = shlex.quote(filename_object),
                libraries = " ".join("-l" + library for library in libraries)
            )
        )

        # access library from compiled code
        self.library = ctypes.cdll.LoadLibrary(filename_shared_object)

    def __getitem__(
        self,
        function
        ):

        if self.library is None:
            assert False, "error"

        return getattr(self.library, function)
