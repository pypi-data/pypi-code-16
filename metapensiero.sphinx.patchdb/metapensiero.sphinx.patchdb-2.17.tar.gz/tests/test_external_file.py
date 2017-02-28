# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Content in external file test
# :Created:   mar 23 feb 2016 11:40:22 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from __future__ import unicode_literals

import fixtures


SQL = """
create table sl_test (
  id integer primary key
)
"""

class TestExternalFile(fixtures.BaseTestCase):
    TEST_TXT = """
    Basic Test
    ==========

    .. patchdb:script:: Create first table
       :file: test.sql
    """

    OTHER_FILES = (('test.sql', SQL),)
