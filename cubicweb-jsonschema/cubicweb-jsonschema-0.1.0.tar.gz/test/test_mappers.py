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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import unittest

import jsl

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_jsonschema import CREATION_ROLE, EDITION_ROLE
from cubicweb_jsonschema.entities.mappers import yams_match


class RelationMapperTC(CubicWebTC):

    def test_target_types(self):
        with self.admin_access.client_cnx() as cnx:
            mapper = cnx.vreg['components'].select(
                'jsonschema.map.relation', cnx,
                etype='CWEType', rtype='add_permission', role='subject',
                target_types={'CWGroup', 'RQLExpression'})
            self.assertCountEqual(mapper.target_types, ['CWGroup', 'RQLExpression'])

            mapper = cnx.vreg['components'].select(
                'jsonschema.map.relation', cnx,
                etype='CWEType', rtype='add_permission', role='subject',
                target_types={'CWGroup'})
            self.assertEqual(mapper.target_types, ['CWGroup'])

    def test_multiple_target_types_inlined(self):
        with self.admin_access.client_cnx() as cnx:
            mapper = cnx.vreg['components'].select(
                'jsonschema.map.relation', cnx,
                etype='CWUser', rtype='use_email', role='subject',
                target_types={'EmailAddress', 'EmailAlias'})
            field = mapper.jsl_field(CREATION_ROLE)
            self.assertIsInstance(field, jsl.fields.ArrayField)
            self.assertIsInstance(field.items, jsl.fields.OneOfField)
            self.assertEqual(len(field.items.fields), 2)

    def test_attribute_have_no_target_types(self):
        with self.admin_access.client_cnx() as cnx:
            mapper = cnx.vreg['components'].select(
                'jsonschema.map.relation', cnx,
                etype='CWUser', rtype='login', role='subject', target_types={'String'})
            self.assertCountEqual(mapper.target_types, [])

    def test_password_field_not_required_on_update(self):
        with self.admin_access.client_cnx() as cnx:
            mapper = cnx.vreg['components'].select(
                'jsonschema.map.relation', cnx,
                etype='CWUser', rtype='upassword', role='subject', target_types={'Password'})
            self.assertTrue(mapper.jsl_field(CREATION_ROLE).required)
            self.assertFalse(mapper.jsl_field(EDITION_ROLE).required)


class ETypeMapperTC(CubicWebTC):

    def test_custom_fields(self):
        with self.admin_access.cnx() as cnx:
            mapper = cnx.vreg['components'].select(
                'jsonschema.map.etype', cnx, etype='Photo')
            self.assertEqual([name for name, _ in mapper.fields],
                             ['data', 'latitude', 'longitude'])
            adapter = cnx.vreg['adapters'].select(
                'IJSONSchema', cnx, etype='Photo')
            schema = adapter.creation_schema()
            defn = schema['definitions']['Photo']
            props = defn['properties']
            self.assertEqual(props['latitude'], {'type': 'number'})
            self.assertEqual(props['longitude'], {'type': 'number'})
            self.assertIn('latitude', defn['required'])
            # "data" is in properties
            self.assertIn('data', props)
            self.assertEqual(props['data'],
                             {'format': 'data-url',
                              'type': 'string',
                              'title': u'data'})
            # but not in "required", per custom entry in fields
            self.assertNotIn('data', defn['required'])


class PredicatesTC(unittest.TestCase):

    def test_yams_match_base(self):
        predicate = yams_match(etype='etype', rtype='rtype', role='role')

        self.assertEqual(predicate(None, None,
                                   etype='etype', rtype='rtype', role='role',
                                   target_types={'CWGroup'}),
                         1)
        self.assertEqual(predicate(None, None,
                                   etype='notetype', rtype='rtype', role='role',
                                   target_types={'CWGroup'}),
                         0)
        self.assertEqual(predicate(None, None,
                                   etype='etype', rtype='notrtype', role='role',
                                   target_types={'CWGroup'}),
                         0)
        self.assertEqual(predicate(None, None,
                                   etype='etype', rtype='rtype', role='notrole',
                                   target_types={'CWGroup'}),
                         0)

    def test_yams_match_target_types(self):
        predicate = yams_match(target_types='String')

        self.assertEqual(predicate(None, None,
                                   etype='etype', rtype='rtype', role='role',
                                   target_types={'CWGroup'}),
                         0)
        self.assertEqual(predicate(None, None,
                                   etype='etype', rtype='rtype', role='role',
                                   target_types={'String'}),
                         1)
        predicate = yams_match(target_types={'CWUser', 'CWGroup'})
        self.assertEqual(predicate(None, None,
                                   etype='etype', rtype='rtype', role='role',
                                   target_types={'CWUser', 'CWGroup'}),
                         1)
        self.assertEqual(predicate(None, None,
                                   etype='etype', rtype='rtype', role='role',
                                   target_types={'CWUser'}),
                         1)


if __name__ == '__main__':
    unittest.main()
