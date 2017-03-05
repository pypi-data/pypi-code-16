"""
pypass.generator.diceware - contains a diceware wordlist interface along with a generator

NOTE: the generator somewhat defeats the purpose of using diceware, use with caution
"""
from __future__ import print_function

import collections
import re
import sqlite3
from os import path
from random import SystemRandom

import requests


class Diceware(collections.Mapping):
    """
    A representation of the Diceware word list

    Uses a SQLite database under the covers to avoid having a whole structure in memory. Access options:

    dice = Diceware()
    dice.word(id) - provide a 5-die roll as int (e.g. 11346) or str (e.g. "11346"), returns that word
    dice[id] - another way to access .word(id)

    dice.random() - get a random word as a string
    dice.random(5) - get several random words as a list of strings

    Random number generation is done with a class-level instance of random.SystemRandom(), which uses urandom
    under the covers for cryptographically-sufficent randomness
    """
    valid_id_re = re.compile("^[1-6]{5}$")
    rng = SystemRandom()

    def __init__(self):
        self._dbfile = path.join(path.dirname(__file__), 'diceware.sqlite')
        self._database = sqlite3.connect(self._dbfile)

    def word(self, index):
        """
        Returns a word corresponding to a given diceware roll (a sequence of five d-6 rolls)

        :param index: a str or int representing the roll, e.g. 16254
        :return str: the word corresponding to the roll
        """
        with self._database as conn:
            cur = conn.cursor()
            cur.execute("SELECT word FROM words WHERE id = ?", (index,))
            results = cur.fetchall()

        if len(results) <= 0:
            return None
        elif len(results) > 1:
            raise RuntimeError("Expected exactly 1 result, got {}; database may be corrupt".format(len(results)))
        else:
            return results[0][0]

    def _roll_die(self):
        """
        Rolls a single die
        :return int: between 1 and 6, inclusive of both
        """
        return self.rng.randint(1, 6)

    def roll(self):
        """
        Produce a diceware roll for one word. Rolls a die 5 times

        :return str: a string representing the roll, e.g. "45632"; always length=5
        """
        rollstr = ""
        for a in range(0, 5):
            rollstr += str(self._roll_die())
        return rollstr

    def random(self, count=1):
        """
        Produces one or more random diceware words from the list.

        For each word to be selected, uses .roll() to generate a roll.

        :param count: and integer that specifies the number of random words to choose
        :return str: if 1 word is requested (default), returns that word as a string
        :return list: if more than one word is requested, returns a list of strings
        """
        if count == 1:
            return self.word(self.roll())
        elif count > 1:
            words = []
            for x in range(0, count):
                words.append(self.random(1))
            return words
        raise ValueError("Must ask for a positive number of words")

    def __getitem__(self, key):
        return self.word(self.__keytransform__(key))

    def __iter__(self):
        for a in range(1, 7):
            for b in range(1, 7):
                for c in range(1, 7):
                    for d in range(1, 7):
                        for e in range(1, 7):
                            yield int("{}{}{}{}{}".format(a, b, c, d, e))

    def __len__(self):
        with self._database as conn:
            cur = conn.cursor()
            cur.execute("SELECT count(id) FROM words")
            result = cur.fetchone()
            return result[0]

    def __keytransform__(self, key):
        if not self.valid_id_re.search(str(key)):
            raise KeyError("'{}' is not a valid diceware index")
        return int(key)


# noinspection PyProtectedMember
def _create_schema(dw_obj=None):
    """
    Utility function to create the SQLite database schema. Shouldn't need to use unless you're creating
    your own, non-default database for some reason (such as from an alternate word list)

    :param dw_obj: a Diceware object. If None, instantiates one with defaults
    :return:
    """
    if dw_obj is None:
        dw_obj = Diceware()

    with dw_obj._database as conn:
        conn.execute("CREATE TABLE WORDS (id INTEGER PRIMARY KEY, word TEXT NOT NULL)")
        conn.commit()


# noinspection PyProtectedMember
def _fill_database(dw_obj=None, wordlist_url='http://world.std.com/~reinhold/diceware.wordlist.asc'):
    """
    Downloads the wordlist file and inserts the words into an existing SQLite database.

    By default, fetches the official diceware wordlist; you can alter this, by pointing to a URL with a
    diceware-format alternate text file.

    :param dw_obj: a Diceware object. If None, instantiates one with defaults
    :param wordlist_url: a URL pointing at a text file containing space-separated rows of roll and word
    :return:
    """
    if dw_obj is None:
        dw_obj = Diceware()

    response = requests.get(wordlist_url)

    with dw_obj._database as conn:
        line_ok_regex = re.compile("^(\d{5})\s+(.+)\s*$")
        line_count = 0
        for line in response.text.splitlines():
            match = line_ok_regex.search(line)
            if not match:
                continue  # line does not contain a diceware word
            index = match.group(1).strip()
            word = match.group(2).strip().lower()
            conn.execute("INSERT INTO words (id, word) VALUES (?, ?)", (int(index), word))
            line_count += 1
            if line_count % 50 == 0:
                print("X", end="")
                conn.commit()

        print("")
        conn.commit()
