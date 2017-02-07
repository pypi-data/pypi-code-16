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

"""cubicweb-jsonschema entities tests"""

from six import text_type

from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_jsonschema.entities.ijsonschema import (
    jsonschema_validate, visible_fields, collection_schema, build_document_tree)


def jsonschema_adapter(cnx, **ctx):
    """Return a IJSONSchema adapter selected from ``ctx`` information."""
    return cnx.vreg['adapters'].select('IJSONSchema', cnx, **ctx)


class MiscTC(CubicWebTC):
    """Tests for functions in entities module."""

    def test_visible_fields(self):
        expected_fields_name = ['firstname', 'surname', 'last_login_time',
                                'in_group', 'use_email']
        with self.admin_access.cnx() as cnx:
            user = cnx.find('CWUser', login=u'admin').one()
            fields_name = [rtype for rtype, _, _ in visible_fields(cnx, user)]
            self.assertCountEqual(fields_name, expected_fields_name)
            self.create_user(cnx, u'bob')
            cnx.commit()
        with self.new_access(u'bob').cnx() as cnx:
            user = cnx.find('CWUser', login=u'admin').one()
            fields_name = [rtype for rtype, _, _ in visible_fields(cnx, user)]
            self.assertCountEqual(fields_name, expected_fields_name)

    def test_visible_fields_account_for_uicfg(self):
        with self.admin_access.cnx() as cnx:
            fields = dict(
                (rtype, targets)
                for rtype, _, targets in visible_fields(cnx, etype='CWUser'))
            # EmailAlias no in, per uicfg.
            self.assertEqual(fields['use_email'], {'EmailAddress'})

    def test_collection_schema(self):
        j_schema = collection_schema('A-name', 'A title')
        expected = {
            'definitions': {
                'A-name': {
                    'type': 'array',
                    'title': 'A title',
                    'items': {
                        'properties': {
                            'id': {'type': 'string'},
                            'title': {'type': 'string'},
                            'url': {'format': 'uri', 'type': 'string'},
                        },
                        'type': 'object'},
                },
            },
            '$ref': '#/definitions/A-name',
        }
        self.assertEqual(j_schema, expected)

    def test_document_tree_nested(self):
        with self.admin_access.cnx() as cnx:
            relinfo = [('picture', 'subject', {'Photo'})]
            document = build_document_tree(cnx, 'CWUser', relinfo, 'creation')
            j_schema = document.get_schema()
        self.assertIn('thumbnail', j_schema['definitions']['Photo']['properties'])
        self.assertIn('Thumbnail', j_schema['definitions'])


class IJSONSchemaETypeAdapterTC(CubicWebTC):

    def test_adapter_from_etype_uicfg(self):
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            self.assertIsNotNone(adapter)
            j_schema = adapter.creation_schema()
        user_props = j_schema['definitions']['CWUser']['properties']
        self.assertIn(u'firstname', user_props)
        self.assertNotIn(u'lastname', user_props)  # per uicfg
        self.assertNotIn(u'surname', user_props)  # per uicfg

    def test_adapter_from_etype_view_schema(self):
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            j_schema = adapter.view_schema()
        self.assertNotIn('EmailAlias', j_schema['definitions'])  # per uicfg
        user_def = j_schema['definitions']['CWUser']
        self.assertNotIn('required', user_def)
        user_props = user_def['properties']
        self.assertIn('use_email', user_props)
        self.assertNotIn(u'login', user_props)  # per uicfg
        emailaddr_def = j_schema['definitions']['EmailAddress']
        self.assertNotIn('use_email', emailaddr_def['properties'])

    def test_target_of_relation_registered(self):
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            j_schema = adapter.creation_schema()
        self.assertNotIn('CWGroup', j_schema['definitions'])
        j_user_schema = j_schema['definitions']['CWUser']['properties']
        self.assertEqual(j_user_schema['in_group']['items']['properties'],
                         {'id': {'type': 'string'},
                          'title': {'type': 'string'},
                          'url': {'format': 'uri', 'type': 'string'}})

    def test_target_of_relation_in_inlined_autoform_section(self):
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            j_schema = adapter.creation_schema()
        self.assertIn('EmailAddress', j_schema['definitions'])

    def test_target_of_relation_has_a_bytes_attribute(self):
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            j_schema = adapter.creation_schema()
        self.assertIn('Photo', j_schema['definitions'])
        photo_schema = j_schema['definitions']['Photo']
        self.assertEqual(photo_schema['properties']['data']['format'],
                         'data-url')

    def test_target_of_relation_of_relation_registered(self):
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            j_schema = adapter.creation_schema()
        self.assertIn('Thumbnail', j_schema['definitions'])

    def test_etype_validate(self):
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            schema = adapter.creation_schema()
            instance = {'login': 1, 'upassword': '123'}
            with self.assertRaises(ValidationError) as cm:
                jsonschema_validate(schema, instance)
            self.assertIn("1 is not of type 'string'", str(cm.exception))

    def test_create_entity(self):
        with self.admin_access.cnx() as cnx:
            group = cnx.find('CWGroup', name=u'users').one()
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            instance = {
                u'login': u'bob',
                u'upassword': u'123',
                u'firstname': u'Bob',
            }
            user = adapter.create_entity(instance)
            # Create `in_group` relationship by hand because it is not
            # included in JSON schema (not inlined).
            user.cw_set(in_group=group)
            cnx.commit()
            for attrname, value in instance.items():
                self.assertEqual(getattr(user, attrname), value)

    def test_schema_role_required(self):
        """Depending on schema role, required field should not be set."""
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            creation_schema = adapter.creation_schema()
            view_schema = adapter.view_schema()
        # 'required' only present in 'creation' schema.
        for defval in view_schema['definitions'].values():
            self.assertNotIn('required', defval)
            self.assertIn('properties', defval)
        self.assertCountEqual(
            creation_schema['definitions']['CWUser']['required'],
            ['login', 'upassword'])


class IJSONSchemaRelationTargetETypeAdapterTC(CubicWebTC):

    def test_filtered_relinfo(self):
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(
                cnx, etype='CWUser', rtype='in_group', role='subject')
            self.assertIsNotNone(adapter)
            relinfos = [(rtype, role) for rtype, role, _ in adapter.relinfo_for('creation')]
            self.assertNotIn(('in_group', 'subject'), relinfos)
            creation_schema = adapter.creation_schema()
            view_schema = adapter.view_schema()
        creation_props = creation_schema['definitions']['CWUser']['properties']
        self.assertTrue(creation_props)  # Ensure it's not empty.
        self.assertNotIn('in_group', creation_props)
        view_props = view_schema['definitions']['CWUser']['properties']
        self.assertIn('in_group', view_props)

    def test_creation_set_relation(self):
        with self.admin_access.cnx() as cnx:
            adapter = jsonschema_adapter(
                cnx, etype='CWUser', rtype='in_group', role='subject')
            group = cnx.find('CWGroup', name=u'users').one()
            user = adapter.create_entity(
                {u'login': u'bob', u'upassword': u'bob'}, group)
            cnx.commit()
            self.assertEqual([x.eid for x in user.in_group], [group.eid])
            with self.assertRaises(ValidationError) as cm:
                adapter.create_entity(
                    {u'login': u'bob', u'upassword': u'bob', 'in_group': group.eid},
                    group)
                cnx.commit()
            self.assertIn("'in_group' was unexpected", str(cm.exception))


class IJSONSchemaEntityAdapterTC(CubicWebTC):

    def test_adapter_from_entity(self):
        with self.admin_access.cnx() as cnx:
            user = cnx.find('CWUser', login=u'admin').one()
            adapter = user.cw_adapt_to('IJSONSchema')
            self.assertIsNotNone(adapter)
            j_schema = adapter.edition_schema()
        user_props = j_schema['definitions']['CWUser']['properties']
        self.assertNotIn(u'lastname', user_props)

    def test_entity_validate(self):
        with self.admin_access.cnx() as cnx:
            user = cnx.find('CWUser', login=u'admin').one()
            adapter = user.cw_adapt_to('IJSONSchema')
            schema = adapter.edition_schema()
            instance = {'login': 'bob', 'upassword': 1}
            with self.assertRaises(ValidationError) as cm:
                jsonschema_validate(schema, instance, user)
            self.assertEqual(cm.exception.entity, user)
            self.assertIn("1 is not of type 'string'", str(cm.exception))

    def test_edition_schema_role(self):
        with self.admin_access.cnx() as cnx:
            user = cnx.find('CWUser', login=u'admin').one()
            adapter = user.cw_adapt_to('IJSONSchema')
            j_schema = adapter.edition_schema()
            user_props = j_schema['definitions']['CWUser']['properties']
            self.assertIn('upassword', user_props)
            self.assertIn('use_email', user_props)  # in "inlined" autoform_section
            self.assertNotIn('lastname', user_props)  # per uicfg.autoform_section

    def test_entity_create(self):
        with self.admin_access.cnx() as cnx:
            users = cnx.find('CWGroup', name=u'users').one()
            adapter = jsonschema_adapter(cnx, etype='CWUser')
            instance = {'login': 'bob', 'upassword': 'sponge',
                        'in_group': [{'id': text_type(users.eid)}],
                        'use_email': [{'address': 'bob@sponge.com'}]}
            entity = adapter.create_entity(instance)
            self.assertEqual(entity.login, 'bob')
            self.assertEqual(entity.upassword, 'sponge')
            self.assertEqual(len(entity.in_group), 1)
            self.assertEqual(entity.in_group[0].name, 'users')
            self.assertEqual(len(entity.use_email), 1)
            self.assertEqual(entity.use_email[0].address, 'bob@sponge.com')

    def test_entity_update(self):
        with self.admin_access.cnx() as cnx:
            entity = self.create_user(cnx, u'bob', password=u'sponge')
            cnx.commit()
            users = cnx.find('CWGroup', name=u'users').one()
            guests = cnx.find('CWGroup', name=u'guests').one()
            adapter = jsonschema_adapter(cnx, entity=entity)

            instance = {'login': 'bobby',
                        'in_group': [{'id': text_type(users.eid)}],
                        'use_email': [{'address': 'bob@sponge.com'}]}
            adapter.edit_entity(instance)
            entity.cw_clear_all_caches()
            self.assertEqual(entity.login, 'bobby')
            # ensure password have not been reseted
            with cnx.security_enabled(read=False):
                self.assertTrue(entity.upassword)
            self.assertEqual(len(entity.in_group), 1)
            self.assertEqual(entity.in_group[0].name, 'users')
            self.assertEqual(len(entity.use_email), 1)
            self.assertEqual(entity.use_email[0].address, 'bob@sponge.com')

            instance = {'login': 'bobby',
                        'in_group': [{'id': text_type(users.eid)},
                                     {'id': text_type(guests.eid)}],
                        'use_email': [{'address': 'bobby@sponge.com'}]}
            adapter.edit_entity(instance)
            entity.cw_clear_all_caches()
            self.assertEqual(entity.login, 'bobby')
            self.assertEqual(len(entity.in_group), 2)
            self.assertCountEqual([group.name for group in entity.in_group],
                                  ['users', 'guests'])
            self.assertEqual(len(entity.use_email), 1)
            self.assertEqual(entity.use_email[0].address, 'bobby@sponge.com')

            instance = {'login': 'bobby',
                        'in_group': [{'id': text_type(users.eid)}],
                        'use_email': [{'address': 'bobby@sponge.com'},
                                      {'address': 'bob.sponge@sponge.com'}]}
            adapter.edit_entity(instance)
            entity.cw_clear_all_caches()
            self.assertEqual(len(entity.in_group), 1)
            self.assertEqual(entity.in_group[0].name, 'users')
            self.assertEqual(len(entity.use_email), 2)
            self.assertCountEqual([addr.address for addr in entity.use_email],
                                  ['bobby@sponge.com', 'bob.sponge@sponge.com'])

            instance = {'login': 'bobby',
                        'in_group': [{'id': text_type(users.eid)}],
                        'use_email': [{'address': 'bob.sponge@sponge.com'}]}
            adapter.edit_entity(instance)
            entity.cw_clear_all_caches()
            self.assertEqual(len(entity.use_email), 1)
            self.assertEqual(entity.use_email[0].address, 'bob.sponge@sponge.com')

            entity.cw_set(use_email=cnx.create_entity('EmailAlias'))
            instance = {'login': 'bobby',
                        'in_group': [{'id': text_type(users.eid)}],
                        'use_email': []}
            adapter.edit_entity(instance)
            entity.cw_clear_all_caches()
            self.assertEqual(len(entity.use_email), 1)
            self.assertEqual(entity.use_email[0].cw_etype, 'EmailAlias')

    def test_serialize(self):
        self.maxDiff = None
        with self.admin_access.cnx() as cnx:
            users = cnx.find('CWGroup', name=u'users').one()
            entity = self.create_user(cnx, u'bob', password=u'sponge',
                                      firstname=u'Bob')
            email = cnx.create_entity('EmailAddress', address=u'bob@sponge.com',
                                      reverse_use_email=entity)
            cnx.commit()
            entity.cw_clear_all_caches()
            email.cw_clear_all_caches()

            def base_serialization(entity):
                """Filter out None from ISerializable serialization."""
                data = entity.cw_adapt_to('ISerializable').serialize()
                return dict((k, v) for k, v in data.items()
                            if v is not None)

            # We expect the "base" serialization (the one from ISerializable),
            # plus relation information.
            expected = base_serialization(entity)
            expected.update({
                'in_group': [{'id': text_type(users.eid),
                              'url': users.absolute_url(),
                              'title': users.dc_title()}],
                'use_email': [base_serialization(email)],
            })

            data = entity.cw_adapt_to('IJSONSchema').serialize()
            self.assertEqual(data, expected)


class IJSONSchemaRelatedEntityAdapterTC(CubicWebTC):

    def test_filtered_relinfo(self):
        with self.admin_access.cnx() as cnx:
            email = cnx.create_entity('EmailAddress', address=u'bob@sponge.com')
            self.create_user(cnx, u'bob', use_email=email)
            cnx.commit()
            adapter = jsonschema_adapter(
                cnx, entity=email, rtype='use_email', role='object')
            self.assertIsNotNone(adapter)
            relinfos = [(rtype, role) for rtype, role, _ in adapter.relinfo_for('edition')]
            expected = [('alias', 'subject'), ('address', 'subject')]
            self.assertCountEqual(relinfos, expected)


if __name__ == '__main__':
    import unittest
    unittest.main()
