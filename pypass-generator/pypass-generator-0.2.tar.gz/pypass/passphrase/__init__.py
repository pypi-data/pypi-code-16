"""
Passphrase generator for python

Uses various backends in the pypass.generator.* namespace. A generator object should have a
.random() method that:

 - returns a single, randomly-chosen word
 - returns a list of words if passed a number > 1 as a parameter
"""

from pypass.generator import diceware


class PassphraseGenerator(object):
    """
    Generates passphrases, by default using Diceware

    Allows you to specify a generator (see Generators, below), the number of words, the separator
    to use between them, and callables to transform each word and/or each phrase (see ``.transform.*``)

    By default, generates a 5-word diceware phrase with no separators, and uses no transforms

    Word count (``elements``), separator, word transforms, and phrase transforms can all be specified at
    construction time, or be modified for an instance by changing the object's attributes of the same names.
    Each can also be overridden for a specific call to ``generate()`` by passing arguments to that method.

    Generators:

    A generator is an object that has a `random` method taking an argument for the number of words to
    generate. The `random` method should return a single word by default or if the number of words is 1,
    otherwise it should return a list of words of the requested length.

    See ``pypass.generator.*``

    Transforms:

    A transform is a callable that accepts a string as an argument and returns a transformed version of it.
    See the transform.* functions for generators of common transforms.

    The ``word_transform`` will be called on each word generated as it's added to the phrase. Separators
    are not passed to word transforms.

    The ``phrase_transform`` will be called on the generated phrase before returning it.

    Examples:

        from pypass.passphrase import PassphraseGenerator, transform

        generator = PassphraseGenerator(elements=7, separator='-')
        passphrase = generator.generate()  # 7-word passphrase, separated by '-'

        generator.word_transform = transform.uppercase()  # next generation, each word will be uppercased
    """
    def __init__(self, elements=5, separator='', **kwargs):
        """
        Constructor - configures the object (by default: 5-word, no separator, Diceware)

        Keywords:

        - generator: specify a generator object to use instead of the default
        - word_transform: a callable that will transform each generated word
        - phrase_transform: a callable that will transform the entire phrase

        :param elements: number of words to generate
        :param separator: separator to use
        :param kwargs: configuration arguments
        """
        self.generator = None
        self.elements = elements
        self.separator = separator
        self.word_transform = None
        self.phrase_transform = None

        if 'generator' in kwargs:
            self.generator = kwargs['generator']

        if 'word_transform' in kwargs:
            self.word_transform = kwargs['word_transform']

        if 'phrase_transform' in kwargs:
            self.phrase_transform = kwargs['phrase_transform']

        if self.generator is None:
            self.generator = diceware.Diceware()

    def generate(self, elements=None, separator=None, word_transform=None, phrase_transform=None):
        """
        Generates a passphrase string.

        With no arguments provided, will use the object's settings; these can be overriden on a given
        call using parameters.

        :param elements: number of words for the generator to use
        :param separator: character to place between words
        :param word_transform: transform callable for each word
        :param phrase_transform: transform callable for the entire phrase
        :return: passphrase string
        """
        if elements is None:
            elements = self.elements

        if separator is None:
            separator = self.separator

        if word_transform is None:
            word_transform = self.word_transform

        if phrase_transform is None:
            phrase_transform = self.phrase_transform

        words = self.generator.random(elements)
        if type(words) is not list:
            words = [words]

        if self.word_transform is not None:
            for i in range(0, len(words)):
                words[i] = word_transform(words[i])

        phrase = separator.join(words)

        if self.phrase_transform is not None:
            phrase = phrase_transform(phrase)

        return phrase

    # TODO strength? May need to modify Generator contract
