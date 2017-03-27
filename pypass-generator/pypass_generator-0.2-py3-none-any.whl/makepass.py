from __future__ import print_function
# from sys import stderr, argv
import logging

from pypass.passphrase import PassphraseGenerator, transform

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # TODO change with CLI arg?


def makepass():
    # TODO control generation options
    # right now, this just generates a Diceware password of 4 words, adding 2 digits and a symbol
    generator = PassphraseGenerator(elements=4,
                                    separator='',
                                    word_transform=transform.capitalize(),
                                    phrase_transform=transform.chain(transform.add_numbers(2),
                                                                     transform.leet())
                                    )
    return generator.generate()


def parse_cli_args(*args):
    # TODO parse CLI args to generate a dict of configuration
    pass


if __name__ == '__main__':
    print(makepass())
