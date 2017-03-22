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
"""Functional security tests."""

from cubicweb.devtools.testlib import CubicWebTC

import testutils


class NonManagerUserTC(CubicWebTC):
    """Tests checking that a user in "users" group only can do things.

    Most of the times, we do not call any assertion method and only rely on no
    error being raised.
    """
    assertUnauthorized = testutils.assertUnauthorized

    login = u'bob'

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            self.create_user(cnx, self.login, ('users', ))
            testutils.authority_with_naa(cnx)
            cnx.commit()

    def test_create_update_authorityrecord(self):
        with self.new_access(self.login).cnx() as cnx:
            arecord = testutils.authority_record(cnx, name=u'a')
            cnx.commit()
            arecord.cw_set(record_id=u'123')
            cnx.commit()

    def test_create_update_sedaprofile(self):
        with self.new_access(self.login).cnx() as cnx:
            profile = testutils.setup_profile(cnx)
            cnx.commit()
            profile.cw_set(user_annotation=u'meh')
            cnx.commit()

    def test_create_update_vocabulary(self):
        with self.new_access(self.login).cnx() as cnx:
            scheme = testutils.setup_scheme(cnx, u'my scheme',
                                            u'lab1', u'lab2')
            cnx.commit()
            scheme.add_concept(u'lab3')
            cnx.commit()

    def test_create_update_agent_in_own_organization(self):
        with self.admin_access.cnx() as cnx:
            org = testutils.authority_with_naa(cnx)
            cnx.execute('SET U authority O WHERE U login %(login)s, O eid %(o)s',
                        {'login': self.login, 'o': org.eid})
            cnx.commit()
            authority_eid = org.eid
        with self.new_access(self.login).cnx() as cnx:
            agent = testutils.agent(cnx, u'bob', authority=authority_eid)
            cnx.commit()
            agent.cw_set(name=u'bobby')
            cnx.commit()

    def test_cannot_create_organizationunit(self):
        with self.new_access(self.login).cnx() as cnx:
            with self.assertUnauthorized(cnx):
                testutils.organization_unit(
                    cnx, u'arch', archival_roles=(u'archival', ))

    def test_cannot_modify_activities(self):
        with self.new_access(self.login).cnx() as cnx:
            arecord = testutils.authority_record(cnx, name=u'a')
            cnx.commit()

            activity = arecord.reverse_used[0]

            with self.assertUnauthorized(cnx):
                activity.cw_set(description=u'hacked')

            with self.assertUnauthorized(cnx):
                activity.cw_set(associated_with=cnx.find('CWUser', login='admin').one())

            with self.assertUnauthorized(cnx):
                activity.cw_set(generated=None)

            with self.assertUnauthorized(cnx):
                activity.cw_delete()


class ManagerUserTC(CubicWebTC):
    """Tests checking that a user in "managers" group only can do things.

    Most of the times, we do not call any assertion method and only rely on no
    error being raised.
    """

    def test_create_update_organization(self):
        with self.admin_access.cnx() as cnx:
            org = testutils.authority_with_naa(cnx)
            cnx.commit()
            org.cw_set(name=u'uh')
            cnx.commit()

    def test_create_update_naa(self):
        with self.admin_access.cnx() as cnx:
            test_naa = testutils.naa(cnx)
            cnx.commit()
            test_naa.cw_set(who=u'1')
            cnx.commit()
            naa = cnx.create_entity('ArkNameAssigningAuthority',
                                    who=u'123', what=u'443')
            cnx.commit()
            naa.cw_set(what=u'987')
            cnx.commit()


if __name__ == '__main__':
    import unittest
    unittest.main()
