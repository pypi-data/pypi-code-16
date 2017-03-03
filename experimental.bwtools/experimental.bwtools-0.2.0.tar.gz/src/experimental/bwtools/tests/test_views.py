# -*- coding: utf-8 -*-
'''Setup tests for this package.'''
from experimental.bwtools.testing import EXPERIMENTAL_BWTOOLS_INTEGRATION_TESTING  # noqa
from plone import api
from Products.statusmessages.adapter import _decodeCookieValue

import unittest


class TestViews(unittest.TestCase):
    '''Test that experimental.bwtools is properly installed.'''

    layer = EXPERIMENTAL_BWTOOLS_INTEGRATION_TESTING

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def assertFloatDictEqual(self, expected, observed, msg=None):
        ''' Fixes floating point issues by rounding
        '''
        expected = {k: round(v, 5) for k, v in expected.iteritems()}
        observed = {k: round(v, 5) for k, v in observed.iteritems()}
        return self.assertDictEqual(expected, observed, msg=None)

    def get_view(self, name, cookies={}, headers={}):
        ''' Get a view with a fresh request
        '''
        request = self.request.clone()
        request.cookies.update(cookies)
        request.environ.update(headers)
        return api.content.get_view(
            name=name,
            context=self.portal,
            request=request,
        )

    def test_empty_cookie(self):
        view = self.get_view('bwtools')
        self.assertDictEqual(view.cookiedict, {})
        self.assertEqual(view.quality, 1)
        self.assertTupleEqual(view.known_bad_ips, ())
        self.assertFalse(view.is_bad_ip)
        self.assertEqual(view.ip, '')

    def test_broken_cookie(self):
        view = self.get_view('bwtools', cookies={'_bw': 'undefined'})
        self.assertDictEqual(
            view.cookiedict,
            {
                'delta0': 0,
                'bandwidth': 0,
                'size100': 0,
                'size0': 0,
                'delta100': 0,
            }
        )
        self.assertEqual(view.quality, 0)

    def test_bad_cookie(self):
        view = self.get_view('bwtools', cookies={'_bw': '1000|1|11000|100001'})
        self.assertDictEqual(
            view.cookiedict,
            {
                'bandwidth': 80000.0,
                'delta0': 1.0,
                'delta100': 11.0,
                'size0': 8.0,
                'size100': 800008.0
            }
        )
        view.show_and_redirect()
        value = view.request.response.cookies['statusmessages']['value']
        self.assertListEqual(
            [x.message for x in _decodeCookieValue(value)],
            [u'Estimated BW: 78Kb/s. MDT 1.0s'],
        )
        self.assertEqual(view.quality, 0)

    def test_good_cookie(self):
        view = self.get_view('bwtools', cookies={'_bw': '1|1|11|100001'})
        self.assertFloatDictEqual(
            view.cookiedict,
            {
                'bandwidth': 80000000.0,
                'delta0': 0.001,
                'delta100': 0.011,
                'size0': 8.0,
                'size100': 800008.0
            }
        )
        view.show_and_redirect()
        value = view.request.response.cookies['statusmessages']['value']
        self.assertListEqual(
            [x.message for x in _decodeCookieValue(value)],
            [u'Estimated BW: 78125Kb/s. MDT 0.001s'],
        )
        self.assertEqual(view.quality, 1)

    def test_good_ips(self):
        view = self.get_view('bwtools', headers={'REMOTE_ADDR': '127.0.0.1'})
        self.assertEqual(view.ip, '127.0.0.1')
        self.assertFalse(view.is_bad_ip)
        self.assertEqual(view.quality, 1)

    def test_bad_ips(self):
        pr = api.portal.get_tool('portal_registry')
        orig_bad_ips = pr._records['experimental.bwtools.known_bad_ips'].value
        api.portal.set_registry_record(
            'experimental.bwtools.known_bad_ips',
            (u'127.0.0.1',)
        )
        view = self.get_view('bwtools', headers={'REMOTE_ADDR': '127.0.0.1'})
        self.assertEqual(view.ip, '127.0.0.1')
        self.assertTrue(view.is_bad_ip)
        self.assertEqual(view.quality, 0)
        pr._records['experimental.bwtools.known_bad_ips'].value = orig_bad_ips
