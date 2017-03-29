# -*- coding: utf-8 -*-
import os
import unittest
import json

from paste.deploy import appconfig
from webtest import TestApp
from pyramid import testing
import responses

try:
    from testdata import test_json_outside_flanders, test_json_intersects_flanders
except:
    from tests.testdata import test_json_outside_flanders, test_json_intersects_flanders

try:
    from __init__ import text_, mock_geozoekdiensten_response, mock_geozoekdiensten_get_gemeente_response, get_provincie_results, get_gemeente_results
except:
    from tests import text_, mock_geozoekdiensten_response, mock_geozoekdiensten_get_gemeente_response, get_provincie_results, get_gemeente_results

from oe_geoutils import main

from oe_geoutils.views.exceptions import internal_server_error

here = os.path.dirname(__file__)

test_geom = json.dumps({
            "type": "MultiPolygon",
            "coordinates": [[[[172933.6922879719058983, 174851.14960918109863997],
                              [172930.21180502674542367, 174832.7836931711062789],
                              [172920.64762709615752101, 174848.13247794657945633],
                              [172933.6922879719058983, 174851.14960918109863997]]]],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::31370"
                }
            }
        })


class FunctionalTests(unittest.TestCase):
    def _get_default_headers(self):
        return {'Accept': 'application/json'}

    @classmethod
    def setUpClass(cls):
        cls.settings = appconfig('config:' + os.path.join(here, 'test.ini'))

    def setUp(self):
        self.app = main({}, **self.settings)
        self.testapp = TestApp(self.app)
        responses.add(responses.POST, "https://test-geo.onroerenderfgoed.be/zoekdiensten/administratievegrenzen")

    def tearDown(self):
        self.testapp.reset()

    def test_get_nearest_address(self):
        res = self.testapp.post('/nearest_address', test_geom)
        self.assertEqual('200 OK', res.status)

    def test_get_nearest_address_outside_Flanders(self):
        res = self.testapp.post('/nearest_address', json.dumps(test_json_outside_flanders), expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)

    def test_get_nearest_address_not_found(self):
        res = self.testapp.post('/nearest_address', json.dumps(test_json_intersects_flanders), expect_errors=True)
        self.assertEqual('200 OK', res.status)

    def test_check_in_flanders(self):
        res = self.testapp.post('/check_in_flanders', test_geom)
        self.assertEqual('200 OK', res.status)

    def test_check_within_flanders(self):
        res = self.testapp.post('/check_within_flanders', test_geom)
        self.assertEqual('200 OK', res.status)

    def test_check_in_flanders_no_json_body(self):
        res = self.testapp.post('/check_in_flanders', expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)

    def test_check_in_flanders_validation_failure(self):
        res = self.testapp.post('/check_in_flanders', '{}', expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)

    def test_check_in_flanders_invalid_url(self):
        res = self.testapp.post('/test', '{}', expect_errors=True)
        self.assertEqual('404 Not Found', res.status)

    def test_internal_server_error(self):
        a = Exception()
        internal_server_error(a, testing.DummyRequest())

    @responses.activate
    def test_gemeente(self):
        res = self.testapp.post('/gemeente', test_geom)
        self.assertEqual('200 OK', res.status)
        print(res.text)

    @responses.activate
    def test_gemeente(self):
        responses.add(responses.POST, 'http://geozoekdienst.en', body=json.dumps(get_gemeente_results))
        res = self.testapp.post('/gemeente', test_geom)
        self.assertEqual('200 OK', res.status)
        print(res.text)

    @responses.activate
    def test_provincie(self):
        responses.add(responses.POST, 'http://geozoekdienst.en', body=json.dumps(get_provincie_results))
        res = self.testapp.post('/provincie', test_geom)
        self.assertEqual('200 OK', res.status)
        print(res.text)

    @responses.activate
    def test_check_erfgoedgemeente(self):
        contour = {
            "coordinates": [[[[172933.6922879719, 174851.1496091811], [172930.21180502675, 174832.7836931711],
                              [172920.64762709616, 174848.13247794658], [172933.6922879719, 174851.1496091811]]]],
            "type": "MultiPolygon", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}
        }
        responses.add(
            responses.POST,
            'http://geozoekdienst.en',
            body='[{"naam": "Leuven", "type": "gemeente", "id": "24062"}]', status=200)
        res = self.testapp.post('/check_in_erfgoedgemeente', params=json.dumps(contour),
                                headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        self.assertIn('ok', res.json["status"])

    @responses.activate
    def test_check_erfgoedgemeente_full_overlap(self):
        responses.add(
            responses.POST,
            'http://geozoekdienst.en',
            body='[{"naam": "Koksijde", "type": "gemeente", "id": "38014"}]', status=200)
        contour = {
            "coordinates": [[[[172933.6922879719, 174851.1496091811], [172930.21180502675, 174832.7836931711],
                              [172920.64762709616, 174848.13247794658], [172933.6922879719, 174851.1496091811]]]],
            "type": "MultiPolygon", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}
        }
        res = self.testapp.post('/check_in_erfgoedgemeente', params=json.dumps(contour),
                                headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        self.assertIn('error', res.json["status"])
        self.assertIn('Gelieve de melding in te dienen bij deze gemeente', res.json["message"])

    @responses.activate
    def test_check_erfgoedgemeente_partial_overlap(self):
        responses.add(
            responses.POST,
            'http://geozoekdienst.en',
            body='[{"naam": "Koksijde", "type": "gemeente", "id": "38014"}, '
                 '{"naam": "Nieuwpoort", "type": "gemeente", "id": "38016"}]', status=200)
        contour = {
            "coordinates": [[[[172933.6922879719, 174851.1496091811], [172930.21180502675, 174832.7836931711],
                              [172920.64762709616, 174848.13247794658], [172933.6922879719, 174851.1496091811]]]],
            "type": "MultiPolygon", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}
        }
        res = self.testapp.post('/check_in_erfgoedgemeente', params=json.dumps(contour),
                                headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        self.assertIn('warn', res.json["status"])
        self.assertIn('Gelieve de melding vooronderzoek eveneens in te dienen bij deze gemeente', res.json['message'])



