# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web.views import actions


class ActionTC(CubicWebTC):

    def test_management(self):
        with self.admin_access.cnx() as cnx:
            at = cnx.create_entity('SEDAArchiveTransfer', title=u'hop')
            self.create_user(cnx, 'user')
            cnx.commit()

        with self.admin_access.web_request() as req:
            rset = req.entity_from_eid(at.eid).as_rset()
            actionsdict = self.pactionsdict(req, rset)
            self.assertIn(actions.ManagePermissionsAction, actionsdict['moreactions'])

        with self.new_access('user').web_request() as req:
            rset = req.entity_from_eid(at.eid).as_rset()
            actionsdict = self.pactionsdict(req, rset)
            self.assertNotIn(actions.ManagePermissionsAction, actionsdict['moreactions'])


if __name__ == '__main__':
    import unittest
    unittest.main()
