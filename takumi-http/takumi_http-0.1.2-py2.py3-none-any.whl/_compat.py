# -*- coding: utf-8 -*-


import sys

PY2 = sys.version_info[0] == 2

if PY2:
    integer_types = (int, long)

else:
    integer_types = (int, )
