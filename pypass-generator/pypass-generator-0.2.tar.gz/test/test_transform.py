import re
from unittest import TestCase

from pypass.passphrase import transform


class TestTransform(TestCase):
    def testAddNumbers(self):
        adder = transform.add_numbers(3)
        teststring = adder("hello")
        self.assertTrue(re.search("^hello\d\d\d$", teststring),
                        "Did not add three numbers, got '{}'".format(teststring))

    def testAddSpecial(self):
        adder = transform.add_symbols(4)
        teststring = adder("hello")
        match = re.search("^hello(....)$", teststring)
        self.assertTrue(match, "Did not add four chars")
        for char in list(match.group(1)):
            self.assertTrue(char in transform.symbol_set['ascii'], "{} not in default symbol set".format(char))

        adder = transform.add_symbols(4, symbols='0')
        self.assertEqual("hello0000", adder("hello"), "Did not add custom symbols")

    def testCapitalize(self):
        capper = transform.capitalize()
        testtring = capper("hello")
        self.assertEqual("Hello", testtring, "Didn't capitalize word, got '{}'".format(testtring))

    def testLeet(self):
        leeter = transform.leet(probability=1)
        teststring = leeter("hello")
        self.assertEqual("h3110", teststring, "Didn't leetify word, got '{}'".format(teststring))

        teststring = leeter("aeiout")
        self.assertEqual("43!0u+", teststring, "Didn't leetify word, got '{}'".format(teststring))

    def testChain(self):
        chainer = transform.chain(transform.capitalize(), transform.add_numbers(2))
        teststring = chainer("hello")
        self.assertTrue(re.search("^Hello\d\d$", teststring), "Didn't do both functions, got '{}'".format(teststring))
