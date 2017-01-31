# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from datetime import datetime

from cubicweb.devtools.testlib import CubicWebTC

import testutils


class EACExportTC(CubicWebTC):

    def test_associated_with(self):
        with self.admin_access.client_cnx() as cnx:
            record = testutils.authority_record(cnx, u'My record')
            cnx.create_entity('Activity', agent=u'007', start=datetime.utcnow(),
                              generated=record)
            cnx.commit()
            eac_xml = record.cw_adapt_to('EAC-CPF').dump()
            self.assertIn('<agent>admin</agent>', eac_xml)
            self.assertIn('<agent>007</agent>', eac_xml)


if __name__ == '__main__':
    import unittest
    unittest.main()
