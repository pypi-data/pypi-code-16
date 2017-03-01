# -*- coding: utf-8 -*-

import unittest
from shaman.src.helpers.url_helpers import canonurl

class TestCanonUrl(unittest.TestCase):
    def test_empty_url(self):
        url = ''
        c_url = canonurl(url)
        self.assertTrue('' == c_url)

    def test_correct_eng_url(self):
        url = 'google.com'
        c_url = canonurl(url)
        self.assertTrue('google.com' == c_url)


    def test_correct_eng_url_with_params(self):
        url = 'google.com/some_results/some_some.html?someparam1=12312312&someparam2=12341234'
        c_url = canonurl(url)
        self.assertEquals(url,c_url)

    def test_correct_eng_url_with_slash(self):
        url = 'google.com/'
        c_url = canonurl(url)
        self.assertTrue('google.com/' == c_url)

    def test_correct_eng_url_with_two_slash(self):
        url = 'google.com//'
        c_url = canonurl(url)
        self.assertTrue('google.com//' == c_url)


    def test_correct_rus_url_too_long(self):
        url = u'http://носки.рф/asdfasdfasdfasdfasdfasldkjfbasdkjbasdkjbclaksjdlkamsdlkasdlkjasdlcjknasdlkjfas87df6a9s87df9a8sd7f09asd'
        result_must_be = 'http://xn--h1adiep.xn--p1ai/asdfasdfasdfasdfasdfasldkjfbasdkjbasdkjbclaksjdlkamsdlkasdlkjasdlcjknasdlkjfas87df6a9s87df9a8sd7f09asd'
        c_url = canonurl(url)
        self.assertEqual(result_must_be, c_url)

    def test_correct_eng_url_too_long(self):
        url = 'http://google.com/asdfasdfasdfasdfasdfasldkjfbasdkjbasdkjbclaksjdlkamsdlkasdlkjasdlcjknasdlkjfas87df6a9s87df9a8sd7f09asd'
        c_url = canonurl(url)
        self.assertTrue(url == c_url)

    def test_correct_eng_url_with_dot_at_end(self):
        url = 'google.com.'
        c_url = canonurl(url)
        self.assertTrue('google.com.' == c_url)

    def test_correct_eng_url_with_dot_at_middle(self):
        url = 'google..com'
        # function raises exception on incorrect url
        self.assertRaises(UnicodeError, canonurl, url)

    def test_correct_eng_url_with_dot_at_start(self):
        url = '.google.com'
        self.assertRaises(UnicodeError, canonurl, url)

    def test_correct_eng_url_with_params_unicode(self):
        url = u'google.com/some_results/some_some.html?someparam1=12312312&someparam2=12341234'
        c_url = canonurl(url)
        self.assertEquals(url, c_url)

    def test_correct_rus_url_with_params(self):
        url = u'носки.рф'
        result_must_be = 'xn--h1adiep.xn--p1ai'
        c_url = canonurl(url)
        self.assertEquals(result_must_be,c_url)

    def test_correct_eng_url_1(self):
        url = 'Wesem-light.ru/perednie-tyuning-fary-lp-komplyekt-linzovannye-s-dnevnymi-khodovymi-ognyami-chernye-vnutri-dlya-ford-focus-3-2011---_1'

        c_url = canonurl(url)
        self.assertEquals(url,c_url)

if __name__ == '__main__':
    unittest.main()