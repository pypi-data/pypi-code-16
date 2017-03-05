from unittest import TestCase

from pypass.generator import Diceware
from pypass.passphrase import PassphraseGenerator


class MockGenerator(object):
    def __init__(self):
        pass

    def random(self, count=1):
        words = "the quick brown fox jumped over the lazy dog".split(' ')

        if count < 1:
            raise ValueError("Requires a positive count")
        if count == 1:
            return words[0]
        else:
            retvalue = words[0:count]
            return retvalue


class TestPassphraseGenerator(TestCase):
    def testCreate(self):
        generator = PassphraseGenerator()
        self.assertIsInstance(generator, PassphraseGenerator)
        self.assertIsInstance(generator.generator, Diceware, "Doesn't default to Diceware generator")
        self.assertEqual(5, generator.elements, "Does not default to 5-word phrase")

    def testCreateSetLength(self):
        generator = PassphraseGenerator(elements=3)
        self.assertEqual(3, generator.elements, "Does not set number of elements with constructor arg")

    def testCreateSetGenerator(self):
        generator = PassphraseGenerator(generator=MockGenerator())
        self.assertIsInstance(generator.generator, MockGenerator, "Doesn't allow custom generator at construction")

    def testGeneration(self):
        generator = PassphraseGenerator(generator=MockGenerator(), elements=3)
        phrase = generator.generate()
        self.assertEqual("thequickbrown", phrase, "Doesn't generate expected phrase, got '{}'".format(phrase))

    def testGenerateWithCustomSeparator(self):
        generator = PassphraseGenerator(generator=MockGenerator(), elements=3, separator='-')
        phrase = generator.generate()
        self.assertEqual("the-quick-brown", phrase, "Custom sep in constructor failed, got '{}'".format(phrase))

        phrase = generator.generate(separator='.')
        self.assertEqual("the.quick.brown", phrase, "Custom sep in method failed, got '{}'".format(phrase))

    def testGenerateWithCustomElements(self):
        generator = PassphraseGenerator(generator=MockGenerator(), elements=4)
        phrase = generator.generate()
        self.assertEqual("thequickbrownfox", phrase, "Custom count in constructor failed, got '{}'".format(phrase))

        phrase = generator.generate(elements=3)
        self.assertEqual("thequickbrown", phrase, "Custom count in method failed, got '{}'".format(phrase))

    def testCustomWordTransform(self):
        def capitalize_first(word):
            return word.capitalize()

        def all_caps(word):
            return word.upper()

        generator = PassphraseGenerator(generator=MockGenerator(), elements=2, word_transform=capitalize_first)
        phrase = generator.generate()
        self.assertEqual("TheQuick", phrase, "Custom word transform in constructor failed, got '{}'".format(phrase))

        phrase = generator.generate(word_transform=all_caps)
        self.assertEqual("THEQUICK", phrase, "Custom word transform in method failed, got '{}'".format(phrase))

    def testCustomPhraseTransform(self):
        def add_numbers(phrase):
            return phrase + "42"

        def all_caps(phrase):
            return phrase.upper()

        generator = PassphraseGenerator(generator=MockGenerator(), elements=3, phrase_transform=all_caps)
        phrase = generator.generate()
        self.assertEqual("THEQUICKBROWN", phrase,
                         "Custom phrase transform in constructor failed, got '{}'".format(phrase))

        phrase = generator.generate(phrase_transform=add_numbers)
        self.assertEqual("thequickbrown42", phrase,
                         "Custom phrase transform in method failed, got '{}'".format(phrase))








