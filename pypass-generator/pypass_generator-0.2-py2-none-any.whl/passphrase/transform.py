"""
Provides transformation generators for use with PassphraseGenerator's word_transform and phrase_transform
callables

Examples:

    from pypass.passphrase import transform

    # Add 3 random digits to each generated word
    generator = PassphraseGenerator(word_transform=transform.add_numbers(3))

    # Capitalize the first letter of each word
    generator = PassphraseGenerator(word_transform=transform.capitalize())
"""
from random import SystemRandom

# "Special Symbols" of various sets
symbol_set = {
    'ascii': list("!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~")
}


def add_numbers(count):
    """
    Generates a word/phrase transform that adds ``count`` numbers to the end of a string

    :param count: how many numbers to add
    :return: a function suitable for use as a transform
    """

    rng = SystemRandom()

    def add_number_transform(word):
        retvalue = word
        for n in range(0, count):
            retvalue += str(rng.randint(0, 9))
        return retvalue

    return add_number_transform


def add_symbols(count, symbols='ascii'):
    """
    Generates a word/phrase transform that adds ``count`` randomly-selected
    special symbols to the end of a string

    By default the list of special symbols are printable ASCII symbols from
    https://www.owasp.org/index.php/Password_special_characters

    You can specify a list of symbols from which to choose in one of three ways:

    1. A string that's a key for the dict ``transform.symbol_set``
    2. A string where each character could be used as a symbol
    3. A list of elements to treat as symbols

    :param count: how many numbers to add
    :param symbols: optional, specify list of symbols (see details)
    :return: a function suitable for use as a transform
    """
    if type(symbols) is str:
        if symbols in symbol_set:
            symbols = symbol_set[symbols]
        else:
            symbols = list(symbols)

    rng = SystemRandom()

    def add_symbol_transform(word):
        retvalue = word
        for n in range(0, count):
            retvalue += rng.choice(symbols)
        return retvalue

    return add_symbol_transform


def capitalize():
    """
    Generates a word/phrase transform that capitalizes the first letter of a string

    It might seem weird for this to be a generator, but it keeps it consistent with the interfaces
    in this module

    :return:
    """

    def capify(item):
        return item.capitalize()

    return capify


def leet(probability=0.2):
    """
    Generates a word/phrase transform that "l33tifies" a string.

    :param probability: float - probability of a subsitutable letter getting changed (default=0.2 [20%])
    :return:
    """
    rng = SystemRandom()

    # TODO more substititions
    substitutions = {
        'a': '4',
        'e': '3',
        'i': '!',
        'o': '0',
        'l': '1',
        't': '+'
    }

    def leetify(item):
        retval = ''
        for letter in item:
            nl = letter
            if letter in substitutions and rng.random() < probability:
                nl = substitutions[letter]
            retval += nl

        return retval

    return leetify


def chain(*args):
    """
    Generates a transform that consists of a chain of other transforms

    Example:

        my_transform = chain(add_numbers(2), capitalize())
        generator.generate(word_transform=my_transform)  # e.g. "Hello12There27"

    :param args: other transforms
    :return: callable
    """

    if len(args) < 1:
        raise ValueError("Need at least one transform to chain")

    def chainer(item):
        retval = item
        for transform in args:
            retval = transform(retval)

        return retval

    return chainer
