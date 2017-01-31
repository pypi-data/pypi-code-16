import unittest

from sdklib.compat import cookies
from sdklib.http.session import Cookie


class TestSession(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cookie = Cookie({"Set-Cookie": "chips=ahoy; vienna=finger"})

    def test_as_cookie_header_value(self):
        res = self.cookie.as_cookie_header_value()
        self.assertIn("chips=ahoy", res)
        self.assertIn("vienna=finger", res)

    def test_as_cookie_header_value_none(self):
        cookie = Cookie(None)
        res = cookie.as_cookie_header_value()
        self.assertEqual(res, "")

    def test_get_cookie_morsel(self):
        res = self.cookie.get("chips")
        self.assertEqual(res.value, "ahoy")

    def test_get_cookie(self):
        res = self.cookie.getcookie()
        self.assertTrue(isinstance(res, cookies.SimpleCookie))
