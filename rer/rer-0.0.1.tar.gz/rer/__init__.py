"""Regular expression in regular expression"""

import re

__version__ = '0.0.1'
__author__ = 'Meme Kagurazaka'


def rer(re_string, re_group=0,
       item_continuation=lambda _: _, list_continuation=lambda _: _):
    """rer atom"""

    return lambda x: list_continuation(
        [item_continuation(_.group(re_group))
         for _ in re.compile(re_string).finditer(x)])
