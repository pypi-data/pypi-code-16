from unittest import TestCase
from pypass.generator.diceware import Diceware

import collections
import sqlite3
import re


class TestDiceware(TestCase):
    def test_create(self):
        obj = Diceware()
        self.assertIsInstance(obj, Diceware, "Did not create a Diceware object")
        self.assertIsInstance(obj, collections.Mapping, "Diceware object not inherited from collections.Mapping")
        self.assertIsInstance(obj._database, sqlite3.Connection, "Diceware database is not a SQLite connection")

    def test_lookup(self):
        dice = Diceware()
        self.assertTrue(getattr(dice, 'word'))
        self.assertEqual('abash', dice.word(11131), "Unable to lookup word by int")
        self.assertEqual('abash', dice.word('11131'), "Unable to lookup word by str")

        self.assertEqual('abash', dice[11131], "Unable to dict-style lookup by int")
        self.assertEqual('abash', dice['11131'], "Unable to dict-style lookup by str")

    def test_dict_performance(self):
        dice = Diceware()

        # lookups
        self.assertEqual('abash', dice[11131], "Unable to dict-style lookup by int")
        self.assertEqual('abash', dice['11131'], "Unable to dict-style lookup by str")

        # len
        self.assertEqual(7776, len(dice), "Len did not return 7776")

        # iter
        count = 0
        for i in Diceware():
            if count == 0:
                self.assertEqual(11111, i, "First iter value was not all 1")
            if count == 6:
                self.assertEqual(11121, i, "7th value was not 11121")
                break
            count += 1

    def test_roll(self):
        dice = Diceware()
        self.assertTrue(re.search("^[1-6]{5}$", dice.roll()))

    def test_random_word(self):
        dice = Diceware()
        self.assertTrue(getattr(dice, 'random'))
        self.assertTrue(re.search('^\S+$', dice.random()), "Random selection doesn't appear to be a single word")
        self.assertTrue(type(dice.random(3)) is list, "Random selection of multiple words does not return a list")
        self.assertRaises(ValueError, dice.random, -1)
