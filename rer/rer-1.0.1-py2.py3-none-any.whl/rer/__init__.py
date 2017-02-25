"""Regular expression in regular expression"""

import re

__version__ = '1.0.1'
__author__ = 'Meme Kagurazaka'
__license__ = 'Public Domain'


def rer(re_string, re_group=0,
        item_continuation=lambda _: _, list_continuation=lambda _: _):
    """rer atom

    This function use regular expression string `re_string' and the group
    `regroup' (default 0) to match the `data'. This will evaluates a list,
    a function `item_continuation' will apply to every item of the list,
    a function `list_continuation' will apply to the list. These 2 functions
    do nothing default.

    Return value is a function which can be apply to the `data'.
    Return value can also be used as a `item_continuation' or
    `list_continuation' of another rer recursively.
    """

    return lambda x: list_continuation(
        [item_continuation(_.group(re_group))
         for _ in re.compile(re_string).finditer(x)])
