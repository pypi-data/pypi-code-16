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

"""cubicweb-jsonschema Yams to jsl  unit tests."""

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_jsonschema.views.y2jsl import y2j_etype


class CWYams2JsonTC(CubicWebTC):

    def rtype(self, etype, rtype):
        return self.vreg.schema[etype].rdef(rtype)

    def test_auto_attributes(self):
        with self.admin_access.cnx() as cnx:

            @y2j_etype(self.vreg, cnx)
            class CWUser(object):
                pass

        j_schema = CWUser.get_schema(ordered=True)
        j_props = j_schema['properties']
        # Check attribute list
        self.assertEqual(['__etype__', '__eid__', 'login', 'upassword',
                          'firstname', 'surname', 'last_login_time'],
                         list(j_props))
        self.assertEqual(['__etype__', '__eid__', 'login', 'upassword'],
                         j_schema['required'])
        # Check type and description
        login = self.rtype('CWUser', 'login')
        self.assertEqual(login.description, j_props['login'].get('description'))
        self.assertEqual('string', j_props['login'].get('type'))
        # Check format
        self.assertEqual('string', j_props['last_login_time'].get('type'))
        self.assertEqual('date-time', j_props['last_login_time'].get('format'))
        # Check simple constraint
        firstname = self.rtype('CWUser', 'firstname')
        self.assertEqual(firstname.constraint_by_type('SizeConstraint').max,
                         j_props['firstname'].get('maxLength'))

    def test_auto_relations(self):
        with self.admin_access.cnx() as cnx:

            @y2j_etype(self.vreg, cnx)
            class Workflow(object):
                __filter_in__ = ('name', 'description')

            @y2j_etype(self.vreg, cnx)
            class State(object):
                pass

        j_schema = State.get_schema(ordered=True)
        state_props = j_schema['properties']

        self.assertEqual(['__etype__', '__eid__', 'name', 'description',
                          'state_of'], list(state_props))
        self.assertEqual(state_props['state_of']['items']['properties'],
                         {'id': {'type': 'string'},
                          'title': {'type': 'string'},
                          'url': {'format': 'uri', 'type': 'string'}})
        self.assertEqual(state_props['state_of']['minItems'], 1)
        self.assertEqual(state_props['state_of']['maxItems'], 1)

    def test_bytes_attributes(self):
        with self.admin_access.cnx() as cnx:

            @y2j_etype(self.vreg, cnx)
            class Photo(object):
                pass

        j_schema = Photo.get_schema(ordered=True)
        properties = j_schema['properties']
        self.assertIn('data', properties)
        self.assertEqual(properties['data']['format'], 'data-url')

    def test_reverse_relation(self):
        with self.admin_access.cnx() as cnx:

            @y2j_etype(self.vreg, cnx)
            class CWUser(object):
                pass

            @y2j_etype(self.vreg, cnx)
            class CWGroup(object):
                __filter_in__ = ('reverse_in_group', )

        j_schema = CWGroup.get_schema(ordered=True)
        properties = j_schema['properties']
        self.assertIn('in_group', properties)
        self.assertEqual(properties['in_group']['items']['properties'],
                         {'id': {'type': 'string'},
                          'title': {'type': 'string'},
                          'url': {'format': 'uri', 'type': 'string'}})

    def test_custom_attribute(self):
        with self.admin_access.cnx() as cnx:

            @y2j_etype(self.vreg, cnx)
            class CWUser(object):
                upassword = {'min_length': 7}

        j_schema = CWUser.get_schema(ordered=True)
        j_props = j_schema['properties']
        self.assertIn('minLength', j_props['upassword'])
        self.assertEqual(7, j_props['upassword']['minLength'])

    def test_custom_relation(self):
        with self.admin_access.cnx() as cnx:

            @y2j_etype(self.vreg, cnx)
            class CWGroup(object):
                pass

            @y2j_etype(self.vreg, cnx)
            class CWUser(object):
                in_group = {'min_items': 1}

        j_schema = CWUser.get_schema(ordered=True)
        user_props = j_schema['properties']
        self.assertIn('in_group', user_props)
        self.assertEqual(1, user_props['in_group']['minItems'])

    def test_default_value_and_vocabulary(self):
        self.config.i18ncompile(['fr'])
        self.config._gettext_init()
        _, __ = self.config.translations['fr']

        with self.admin_access.cnx() as cnx:
            cnx._ = _

            @y2j_etype(self.vreg, cnx)
            class CWDataImport(object):
                pass

        j_status = CWDataImport.get_schema(ordered=True)['properties']['status']
        self.assertEqual('in progress', j_status.get('default'))
        self.assertEqual([u'en cours', u'succ\xe8s', u'\xe9chec'],
                         j_status.get('options', {}).get('enum_titles'))


if __name__ == '__main__':
    import unittest
    unittest.main()
