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
from typing import Any, Dict, List


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


# =============================================================================
# Dictionaries
# =============================================================================

def merge_dicts(*dict_args: Dict) -> Dict:
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    # http://stackoverflow.com/questions/38987
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def rename_keys(d: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Renames keys in a dictionary according to the mapping to -> from.
    Leave other keys unchanged.
    """
    result = {}  # type: Dict[str, Any]
    for k, v in d.items():
        if k in mapping:
            k = mapping[k]
        result[k] = v
    return result


def prefix_dict_keys(d: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """
    Returns a dictionary that's the same as d but with prefix prepended to its
    keys.
    """
    result = {}  # type: Dict[str, Any]
    for k, v in d.items():
        result[prefix + k] = v
    return result
