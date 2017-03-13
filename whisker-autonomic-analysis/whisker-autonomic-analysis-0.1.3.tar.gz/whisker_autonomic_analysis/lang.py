#!/usr/bin/env python
# whisker_autonomic_analysis/lang.py

"""
===============================================================================
    Copyright (C) 2017-2017 Rudolf Cardinal (rudolf@pobox.com).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
===============================================================================
"""

import pprint
from typing import Any, List


# =============================================================================
# RNC repr aids to save typing later
# =============================================================================

def _repr_result(obj: Any, elements: List[str],
                 with_addr: bool = False) -> str:
    if with_addr:
        return "<{qualname}({elements}) at {addr}>".format(
            qualname=obj.__class__.__qualname__,
            elements=", ".join(elements),
            addr=hex(id(obj)))
    else:
        return "{qualname}({elements})".format(
            qualname=obj.__class__.__qualname__,
            elements=", ".join(elements))


def auto_repr(obj: Any, with_addr: bool = False) -> str:
    """
    Convenience function for repr().
    Works its way through the object's __dict__ and reports accordingly.
    """
    elements = ["{}={}".format(k, repr(v)) for k, v in obj.__dict__.items()]
    return _repr_result(obj, elements, with_addr=with_addr)


def simple_repr(obj: Any, attrnames: List[str],
                with_addr: bool = False) -> str:
    """
    Convenience function for repr().
    Works its way through a list of attribute names, and creates a repr()
    assuming that parameters to the constructor have the same names.
    """
    elements = ["{}={}".format(name, repr(getattr(obj, name)))
                for name in attrnames]
    return _repr_result(obj, elements, with_addr=with_addr)


def auto_str(obj: Any) -> str:
    return pprint.pformat(obj.__dict__)
