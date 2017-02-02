# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-saem-ref automatic tests


uncomment code below if you want to activate automatic test for your cube:

.. sourcecode:: python

    from cubicweb.devtools.testlib import AutomaticWebTest

    class AutomaticWebTest(AutomaticWebTest):
        '''provides `to_test_etypes` and/or `list_startup_views` implementation
        to limit test scope
        '''

        def to_test_etypes(self):
            '''only test views for entities of the returned types'''
            return set(('My', 'Cube', 'Entity', 'Types'))

        def list_startup_views(self):
            '''only test startup views of the returned identifiers'''
            return ('some', 'startup', 'views')
"""

from functools import partial
from unittest import TestCase
from logilab.common import attrdict

from cubicweb.devtools import testlib

from cubicweb_saem_ref import cwuri_url

import testutils


class CWURI_URLTC(TestCase):

    def test(self):
        class entity(attrdict):
            @property
            def _cw(self):
                return self

            def build_url(self, path):
                return 'http://built/' + path

        self.assertEqual(cwuri_url(entity({'cwuri': 'whatever'})),
                         'whatever')
        self.assertEqual(cwuri_url(entity({'cwuri': 'ark:/123'})),
                         'http://built/ark:/123')
        self.assertEqual(cwuri_url(entity({'cwuri': 'http://domain.org/ark:/123'})),
                         'http://domain.org/ark:/123')


class ArkURLTC(testlib.CubicWebTC):

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            testutils.authority_with_naa(cnx)
            cnx.commit()

    def test_absolute_url_use_ark(self):
        ark_etypes = [eschema.type for eschema in self.schema['ark'].subjects()]
        create_entity_for = {
            'Agent': partial(testutils.agent, name=u'bob'),
            'AuthorityRecord': partial(testutils.authority_record, name=u'rec'),
            'Concept': partial(testutils.concept, label=u'l'),
            'ConceptScheme': partial(testutils.setup_scheme, title=u't'),
            'Organization': partial(testutils.authority_with_naa),
            'OrganizationUnit': partial(testutils.organization_unit, name=u'ou'),
            'SEDAArchiveTransfer': testutils.setup_profile,
        }
        baseurl = self.vreg.config['base-url']
        with self.admin_access.cnx() as cnx:
            testutils.setup_scheme(cnx, u'example', u'l')
            cnx.commit()
            for etype in ark_etypes[:]:
                # with self.subTest(etype=etype):
                entity = create_entity_for[etype](cnx)
                assert entity.ark
                url = entity.absolute_url()
                assert url.startswith(baseurl)
                path = url[len(baseurl):]
                self.assertEqual(path, u'ark:/' + entity.ark)
                ark_etypes.remove(etype)
        if ark_etypes:
            self.fail('entity types not checked {}'.format(ark_etypes))


if __name__ == '__main__':
    import unittest
    unittest.main()
