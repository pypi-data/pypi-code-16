# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test for multiple revisions of script
# :Created:   mer 24 feb 2016 17:30:26 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from __future__ import unicode_literals

import fixtures


FIRST_REV = """
Multiple revisions
==================

.. patchdb:script:: Create first table

   create table test (
     id integer primary key
   )
"""

SECOND_REV = """
Multiple revisions
==================

.. patchdb:script:: Create first table
   :revision: 2

   create table test (
     id integer primary key,
     thevalue integer
   )

.. patchdb:script:: Update first table
   :depends: Create first table@1
   :brings: Create first table@2

   alter table test add thevalue integer
"""


class TestMultipleRevFromScratch(fixtures.BaseTestCase):
    TEST_TXT = SECOND_REV


class TestMultipleRevIncremental(fixtures.BaseTestCase):
    TEST_TXT = FIRST_REV

    def test_1(self):
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute('select thevalue from test')
            except exception as e:
                assert 'THEVALUE' in str(e).upper()
            else:
                assert False, "Should have raised an exception of kind %r!" % exception
        finally:
            connection.close()

    def test_2(self):
        self.build({'test.txt': SECOND_REV})
        output = self.patchdb('--debug')
        self.assertIn('Done, applied 1 script', output)
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            cursor.execute('select thevalue from test')
        finally:
            connection.close()
