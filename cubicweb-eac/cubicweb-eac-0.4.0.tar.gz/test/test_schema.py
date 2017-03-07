# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-eac unit tests for schema"""

import sqlite3
import unittest
from datetime import date
from contextlib import contextmanager

from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_eac import testutils


@contextmanager
def assertValidationError(self, cnx):
    with self.assertRaises(ValidationError) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


class SchemaConstraintsTC(CubicWebTC):
    assertValidationError = assertValidationError

    def test_on_create_set_end_date_before_start_date(self):
        """ create an entity whose end_date is before start_date.
        ValidationError expected
        """
        with self.admin_access.repo_cnx() as cnx:
            with self.assertValidationError(cnx) as cm:
                testutils.authority_record(cnx, u'Arthur',
                                           start_date=date(524, 2, 9),
                                           end_date=date(500, 7, 12))
            self.assertIn("must be less than", str(cm.exception))

    def test_on_update_set_end_date_before_start_date(self):
        """ create a valid entity and update it with a new end_date set before the start_date.
            ValidationError expected
        """
        if sqlite3.sqlite_version_info < (3, 7, 12):
            # with sqlite earlier than 3.7.12, boundary constraints are not checked by the database,
            # hence the constraint is only triggered on start_date modification
            self.skipTest('unsupported sqlite version')
        with self.admin_access.repo_cnx() as cnx:
            agent = testutils.authority_record(cnx, u'Arthur',
                                               start_date=date(454, 2, 9),
                                               end_date=date(475, 4, 12))
            cnx.commit()
            with self.assertValidationError(cnx) as cm:
                agent.cw_set(end_date=date(442, 7, 12))
            self.assertIn("must be less than", str(cm.exception))

    def test_on_update_set_start_date_after_end_date(self):
        """ create an entity without start_date :
            No constraint on the end_date
            update the entity with a start_date set after the start_date :
            ValidationError expected
        """
        with self.admin_access.repo_cnx() as cnx:
            agent = testutils.authority_record(cnx, u'Arthur', end_date=date(476, 2, 9))
            cnx.commit()
            with self.assertValidationError(cnx) as cm:
                agent.cw_set(start_date=date(527, 4, 12))
            self.assertIn("must be less than", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
