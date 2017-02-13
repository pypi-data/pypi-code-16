# -*- coding: utf-8 -*-
import os
import os.path

from nose.tools import assert_equal, assert_not_equal

from pypeline.markup import markup
from pypeline.tests import TestPairwise


from unittest import TestCase
TestCase.maxDiff = None

class TestMarkup(TestPairwise):

    basedir = os.path.join(os.path.dirname(__file__), 'markups')

    """
    test_* methods are run like regular tests
    _test_* methods are run with the allpairs logic (e.g. once for each readme)
        and that is kicked off by test()
    """
    def __init__(self):
        super(TestMarkup, self).__init__()
        self.data = {}
        files = os.listdir(self.basedir)
        for f in files:
            format = os.path.splitext(f)[1].lstrip('.')
            if format == 'html':
                continue
            self.data[format] = f

    def setUp(self):
        pass

    def _test_rendering(self, format):
        readme = self.data[format]
        source_file = open(os.path.join(self.basedir, readme), 'r')
        source = source_file.read().decode('utf-8')
        expected_file = open(os.path.join(self.basedir, '%s.html' % readme),
                             'r')
        expected = expected_file.read().decode('utf-8')
        actual = markup.render(os.path.join(self.basedir, readme))
        #assert_true(isinstance(actual, unicode))
        if source != expected:
            assert_not_equal(source, actual, "Did not render anything.")
        assert_equal(expected, actual)

    def test_can_render(self):
        assert_equal('markdown', markup.can_render('README.markdown'))
        assert_equal('markdown', markup.can_render('README.md'))
        assert_equal(None, markup.can_render('README.cmd'))

    def test_unicode_utf8(self):
        chinese = markup.unicode(u'華語')
        assert_equal(chinese, u'華語')
        assert_equal(type(chinese), unicode)

    def test_unicode_ascii(self):
        ascii = markup.unicode('abc')
        assert_equal(ascii, u'abc')
        assert_equal(type(ascii), unicode)

    def test_unicode_latin1(self):
        latin1 = u'abcdé'.encode('latin_1')
        latin1 = markup.unicode(latin1)
        assert_equal(latin1, u'abcdé')
        assert_equal(type(latin1), unicode)

