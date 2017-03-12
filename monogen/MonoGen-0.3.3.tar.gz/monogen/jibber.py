import string

from random import choice, shuffle
try:
    from secrets import choice as schoice
except ImportError:
    schoice = choice

__all__ = ('generate_word', 'generate_words', 'generate_password')

vowels = 'aeiou'
symbols = '#?!@$%^&><+`*()-]'
alphabet = string.ascii_letters + string.digits + symbols

initial_consonants = tuple(set(string.ascii_uppercase) - set('AEIOU')
                      # remove those easily confused with others
                      - set('QX')
                      # add some crunchy clusters
                      | set(['Bl', 'Br', 'Cl', 'Cr', 'Dr', 'Fl',
                             'Fr', 'Gl', 'Gr', 'Pl', 'Pr', 'Sk',
                             'Sl', 'Sm', 'Sn', 'Sp', 'St', 'Str',
                             'Sw', 'Tr', 'Ch', 'Sh'])
                      )

final_consonants = tuple(set(string.ascii_lowercase) - set(vowels)
                    # remove the confusables
                    - set('qxcsj')
                    # crunchy clusters
                    | set(['ct', 'ft', 'mp', 'nd', 'ng', 'nk', 'nt',
                           'pt', 'sk', 'sp', 'ss', 'st', 'ch', 'sh'])
                    )


def generate_word():
    """Returns a random consonant-vowel-consonant pseudo-word."""
    return ''.join(choice(s) for s in (initial_consonants,
                                       vowels,
                                       final_consonants))


def generate_words(wordcount):
    """Returns a list of ``wordcount`` pseudo-words."""
    return '_'.join([generate_word() for _ in range(wordcount)])


def generate_password(length=16, min_lower=2, min_upper=2, min_num=1, min_sym=1):
    while True:
        password = ''.join(schoice(alphabet) for i in range(length))
        if (sum(c.islower() for c in password) >= min_lower
                and sum(c.isupper() for c in password) >= min_upper
                and sum(c.isdigit() for c in password) >= min_num
                and sum(c in symbols for c in password) >= min_sym):
            return password
