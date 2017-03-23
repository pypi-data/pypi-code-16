import math
import unittest

from typing import Any, List  # NOQA

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import scipy.special  # type: ignore

from .guess import guess_schema


class TestGuess(unittest.TestCase):
    def testBasicSchema(self):
        rs = np.random.RandomState(17)
        test_frame = pd.DataFrame.from_items([
            ('few_numbers', [rs.randint(0, 10) for _ in range(100)]),
            ('more_numbers', [rs.randint(0, 100) for _ in range(100)]),
            ('all_distinct_numbers', [i for i in range(100)]),
            ('all_distinct_strings', [('val' + str(i)) for i in range(100)]),
            ('constant', [1 for _ in range(100)])])
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {'name': 'few_numbers',
                 'stat_type': 'categorical',
                 'values': [{'value': str(x)} for x in range(10)],
                 'stat_type_reason': 'Only 10 distinct values'},
                {'name': 'more_numbers',
                 'stat_type': 'realAdditive',
                 'stat_type_reason':
                     'Contains exclusively numbers (68 of them)'},
                {'name': 'all_distinct_numbers',
                 'stat_type': 'realAdditive',
                 'stat_type_reason':
                     'Contains exclusively numbers (100 of them)'},
                {'name': 'all_distinct_strings',
                 'stat_type': 'void',
                 'stat_type_reason': 'Non-numeric and all values unique'},
                {'name': 'constant',
                 'stat_type': 'void',
                 'stat_type_reason': 'Column is constant'}
            ]
        }
        self.assertEqual(guessed, expected)

    def testTrickyCategoricals(self):
        test_frame = pd.DataFrame.from_items([
            ('foo', [.1, 1.000000002, float('nan'), ""])])
        guessed = guess_schema(test_frame).to_json()
        # NaN doesn't count, but empty string does
        expected = {
            'columns': [
                {'name': 'foo',
                 'stat_type': 'categorical',
                 'values': [
                     {'value': ''},
                     {'value': '0.1'},
                     {'value': '1.000000002'},
                 ],
                 'stat_type_reason': 'Only 3 distinct values'},
            ]
        }
        self.assertEqual(guessed, expected)

    def testNumericCategoricalSorting(self):
        test_frame = pd.DataFrame.from_items([
            ('foo', [0, 1, 'A', 'C', 2, 100, 'B', 20, 'IMASTRING', 'AA', 10])])
        guessed = guess_schema(test_frame).to_json()
        # NaN doesn't count, but empty string does
        expected = {
            'columns': [
                {'name': 'foo',
                 'stat_type': 'categorical',
                 'values': [
                     {'value': '0'},
                     {'value': '1'},
                     {'value': '2'},
                     {'value': '10'},
                     {'value': '20'},
                     {'value': '100'},
                     {'value': 'A'},
                     {'value': 'AA'},
                     {'value': 'B'},
                     {'value': 'C'},
                     {'value': 'IMASTRING'},
                 ],
                 'stat_type_reason': 'Only 11 distinct values'},
            ]
        }
        self.assertEqual(guessed, expected)

    def testTooSparseCategorical(self):
        test_frame = pd.DataFrame.from_items([
            ('foo', ["f{}".format(x) for x in range(100)] * 2)])
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {'name': 'foo',
                 'stat_type': 'void',
                 'stat_type_reason':
                 '100 distinct values. 100 are non-numeric (f0, f1, f2, ...)'},
            ]
        }
        self.assertEqual(guessed, expected)

    def testOneNonNumberAndNull(self):
        vals = list(range(30))  # type: List[Any]
        vals = vals + ['-', np.nan]
        test_frame = pd.DataFrame.from_dict({'foo': vals})
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {'name': 'foo',
                 'stat_type': 'void',
                 'stat_type_reason':
                 '31 distinct values. 1 are non-numeric (-)'},
            ]
        }
        self.assertEqual(guessed, expected)

    def testNormalTransformations(self):
        rs = np.random.RandomState(17)
        n = 10000
        # We want all the columns to have similar properties, i.e. mean and
        # variance. Since logit normals don't have a closed form for those,
        # just pick a sensible logit normal distribution, then use its mean
        # and variance and make normal and log normal distributions to match.
        logit_normal_data = scipy.special.expit(rs.normal(.5, .1, n))
        mean = np.mean(logit_normal_data)
        var = np.var(logit_normal_data)
        m2 = mean ** 2
        # https://en.wikipedia.org/wiki/Log-normal_distribution#Arithmetic_moments
        ln_mean = math.log(m2 / math.sqrt(var + m2))
        ln_var = math.log(var / m2 + 1)
        test_frame = pd.DataFrame.from_items([
            ('normal', rs.normal(mean, math.sqrt(var), n)),
            ('log_normal', rs.lognormal(ln_mean, math.sqrt(ln_var), n)),
            ('logit_normal', logit_normal_data)])
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [
                {'name': 'normal', 'stat_type': 'realAdditive'},
                {'name': 'log_normal', 'stat_type': 'realMultiplicative'},
                {'name': 'logit_normal', 'stat_type': 'proportion'},
            ]
        }
        self.assertEqual(guessed, expected)

    def testLogNormalWithSingleNegativeValue(self):
        rs = np.random.RandomState(17)
        data = rs.lognormal(0, 1, 10000)
        data = np.append(data, -.01)
        test_frame = pd.DataFrame({'almost_log_normal': data})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        # It's not actually for sure true that this should be realAdditive and
        # not realMultiplicative. See the discussion in guess.py.
        expected = {
            'columns': [
                {'name': 'almost_log_normal', 'stat_type': 'realAdditive'}
            ]
        }
        self.assertEqual(guessed, expected)

    def testNumericColumnFullOfStrings(self):
        rs = np.random.RandomState(17)
        test_frame = pd.DataFrame({
            'str_numbers': [str(rs.randint(0, 100)) for _ in range(100)]})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [
                {'name': 'str_numbers', 'stat_type': 'realAdditive'}
            ]
        }
        self.assertEqual(guessed, expected)


if __name__ == '__main__':
    unittest.main()
