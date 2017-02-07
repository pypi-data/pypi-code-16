import json
import jsonschema

from cubicweb.pyramid.test import PyramidCWTest


def find_link(links, rel):
    for link in links:
        if link['rel'] == rel:
            return link
    else:
        raise ValueError('no "{0}" link found in {1}'.format(
            rel, links))


class SchemaRoutesAndViewsTC(PyramidCWTest):

    settings = {
        'cubicweb.bwcompat': False,
    }

    def includeme(self, config):
        config.include('cubicweb_jsonschema.pviews')

    def get_schema(self, path, status=200, **kwargs):
        response = self.webapp.get(
            path, status=status,
            headers={'accept': 'application/schema+json'}, **kwargs)
        if status != 200:
            return None
        schema = response.json
        with open(self.datapath('hyper-schema.json')) as f:
            jsonschema.validate(schema, json.load(f))
        return schema

    def test_application_schema(self):
        self.login()
        res = self.webapp.get('/schema', status=200,
                              headers={'accept': 'application/schema+json'})
        links = res.json['links']
        self.assertCountEqual([link['href'] for link in links],
                              ['/photo/', '/photo/%7Bid%7D'])

    def test_etype_schema_route(self):
        self.login()  # needed to get something in #/definitions/CWUser.
        j_schema = self.get_schema('/cwuser/schema')
        user_def = j_schema['definitions']['CWUser_plural']
        self.assertEqual(user_def['title'], u'CWUser_plural')
        self.assertIn(u'title', user_def['items']['properties'])

    def test_entity_schema_route(self):
        with self.admin_access.cnx() as cnx:
            eid = cnx.find('CWUser', login=u'admin')[0][0]
        self.login()  # Need to access CWUser entity.
        j_schema = self.get_schema('/cwuser/{0}/schema'.format(eid))
        user_props = j_schema['definitions']['CWUser']['properties']
        # As per test/data/entities.py:CWUserIJSONSchemaEntityAdapter and
        # test/data/views.py uicfg.
        self.assertNotIn(u'lastname', user_props)
        self.assertNotIn(u'fistname', user_props)

    def test_etype_hyperschema(self):
        schema = self.get_schema('/cwuser/schema')
        links = schema['links']
        # Use not connected, can only list instances.
        self.assertEqual(len(links), 2)
        list_link = find_link(links, 'instances')
        self.assertEqual(list_link['method'], u'GET')
        self.assertIn('targetSchema', list_link)
        self.assertEqual(list_link['href'], u'/cwuser/')
        self_link = find_link(links, 'self')
        self.assertEqual(self_link['method'], u'GET')
        self.assertEqual(self_link['targetSchema']['$ref'],
                         '/cwuser/schema?role=view')
        # Log in to get rights to create a CWUser.
        self.login()
        schema = self.get_schema('/cwuser/schema')
        links = schema['links']
        self.assertEqual(len(links), 3)
        create_link = find_link(links, 'create')
        self.assertEqual(create_link['method'], u'POST')
        self.assertEqual(create_link['href'], u'/cwuser/')
        self.assertEqual(create_link['schema']['$ref'],
                         '/cwuser/schema?role=creation')

    def test_etype_hyperschema_permissions(self):
        with self.admin_access.cnx() as cnx:
            self.create_user(cnx, u'bob')
            cnx.commit()
        # Non-admin user cannot create CWUser entities, so the "create" link
        # should not appear.
        self.login(u'bob')
        schema = self.get_schema('/cwuser/schema')
        links = schema['links']
        self.assertEqual(len(links), 2)
        self.assertCountEqual(
            [l['rel'] for l in links], [u'instances', u'self'])

    def test_etype_schema_with_roles(self):
        def makerequest(role, status=200):
            return self.get_schema(
                '/cwuser/schema', params={'role': role}, status=status)

        with self.subTest(role='INVALID'):
            makerequest('INVALID', status=400)

        for role in ('view', 'creation'):
            with self.subTest(role=role):
                schema = makerequest(role)
            with self.admin_access.web_request() as req:
                adapter = req.vreg['adapters'].select(
                    'IJSONSchema', req, etype='CWUser')
                expected = getattr(adapter, '{}_schema'.format(role))()
                # Just check lenght as comparison of dict is tedious w.r.t.
                # ordering.
                self.assertEqual(len(schema), len(expected))

    def test_entity_hyperschema(self):
        with self.admin_access.cnx() as cnx:
            eid = cnx.find('CWSource')[0][0]
        schema = self.get_schema('/cwsource/{0}/schema'.format(eid))
        links = schema['links']
        # Use not connected, can only get "self".
        self.assertEqual(len(links), 2)
        self_link = find_link(links, 'self')
        self.assertEqual(self_link['method'], u'GET')
        self.assertIn('targetSchema', self_link)
        self.assertEqual(self_link['href'], u'/cwsource/{0}/'.format(eid))
        up_link = find_link(links, 'up')
        self.assertEqual(up_link['method'], u'GET')
        # Log in to get rights to create a CWUser.
        self.login()
        schema = self.get_schema('/cwsource/{0}/schema'.format(eid))
        links = schema['links']
        self.assertEqual(len(links), 4)
        href = '/cwsource/{0}/'.format(eid)
        edition_link = find_link(links, 'edit')
        self.assertEqual(edition_link['method'], u'PATCH')
        self.assertEqual(edition_link['href'], href)
        self.assertEqual(edition_link['schema']['$ref'],
                         '/cwsource/{0}/schema?role=edition'.format(eid))
        self.assertIn('schema', edition_link)
        delete_link = find_link(links, 'delete')
        self.assertEqual(delete_link['rel'], u'delete')
        self.assertEqual(delete_link['method'], u'DELETE')
        self.assertEqual(delete_link['href'], href)
        self.assertNotIn('schema', delete_link)

    def test_entity_hyperschema_permissions(self):
        with self.admin_access.cnx() as cnx:
            eid = cnx.find('CWSource')[0][0]
            self.create_user(cnx, u'bob')
            cnx.commit()
        # User not admin, cannot update/delete a CWSource.
        self.login(u'bob')
        schema = self.get_schema('/cwsource/{0}/schema'.format(eid))
        links = schema['links']
        self.assertEqual(len(links), 2)
        self_link = find_link(links, 'self')
        self.assertEqual(self_link['href'], '/cwsource/{0}/'.format(eid))
        up_link = find_link(links, 'up')
        self.assertEqual(up_link['href'], '/cwsource/')
        self.assertEqual(up_link['targetSchema']['$ref'], '/cwsource/schema')

    def test_entity_schema_with_roles(self):
        with self.admin_access.cnx() as cnx:
            eid = cnx.find('CWSource')[0][0]

        def makerequest(role, status=200):
            return self.get_schema(
                '/cwsource/{0}/schema'.format(eid), params={'role': role},
                status=status)

        with self.subTest(role='creation'):
            makerequest('creation', status=400)

        for role in ('view', 'edition'):
            with self.subTest(role=role):
                schema = makerequest(role)
            with self.admin_access.web_request() as req:
                entity = req.entity_from_eid(eid)
                adapter = entity.cw_adapt_to('IJSONSchema')
                expected = getattr(adapter, '{}_schema'.format(role))()
                # Just check lenght as comparison of dict is tedious w.r.t.
                # ordering.
                self.assertEqual(len(schema), len(expected))


if __name__ == '__main__':
    import unittest
    unittest.main()
