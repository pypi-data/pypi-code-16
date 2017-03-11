#!python3
import math
import sys
import unittest

sys.path.insert(0, '../area_under_curve/')

import area_under_curve as auc
auc.LOGGING = False

class BoundsTest(unittest.TestCase):
    """Test class for Bounds class"""
    def test_bounds_ok(self):
        """basic bounds check"""
        bounds_ok = auc.Bounds(2, 4, .1)
        assert bounds_ok.lower_bound == 2
        assert bounds_ok.upper_bound == 4
        assert bounds_ok.step_size == .1
        assert len(bounds_ok.full_range) == 21

    def test_bad_step_size(self):
        """reject invalid step size"""
        with self.assertRaises(ValueError):
            auc.Bounds(2, 4, 0)

    def test_bad_step_size_2(self):
        """reject invalid step size"""
        with self.assertRaises(ValueError):
            auc.Bounds(2, 4, -.1)

    def test_bad_bounds(self):
        """reject if lower bound <= upper bound"""
        with self.assertRaises(ValueError):
            auc.Bounds(2, 2, 1)

    def test_bad_bounds_2(self):
        """reject if lower bound <= upper bound"""
        with self.assertRaises(ValueError):
            auc.Bounds(2, 1, 1)

    def test_bounds_string_rep(self):
        """test string representation of bounds"""
        bounds = auc.Bounds(-2, 2.5, .1)
        bounds_str = str(bounds)
        assert bounds_str == "Bounds: [-2 - 2.5], step_size: 0.1"

class PolynomialTest(unittest.TestCase):
    """Test class for Bounds class"""
    def test_int_ok(self):
        """correctly evaluate valid polynomial"""
        polynomial_ok = auc.Polynomial({2:3, 1:4, 0:5})
        assert polynomial_ok.evaluate(-2) == 9
        assert polynomial_ok.evaluate(0) == 5
        assert polynomial_ok.evaluate(2) == 25

    def test_string_rep_ok_1(self):
        """test string reprentation of polynomial"""
        polynomial_1 = auc.Polynomial({0:-2.5, 1:1.5, 3:2, 4:1})
        assert str(polynomial_1) == "f(x)=x^4 + 2x^3 + 1.5x + -2.5"

    def test_zero_ok(self):
        """correctly evaluate valid polynomial f(x)=0"""
        polynomial_ok = auc.Polynomial({0:0})
        assert polynomial_ok.evaluate(5) == 0
        assert str(polynomial_ok) == "f(x)=0"

    def test_string_rep_ok_2(self):
        """test string reprentation of polynomial"""
        polynomial_1 = auc.Polynomial({0:5})
        assert str(polynomial_1) == "f(x)=5"

    def test_constant_ok(self):
        """correctly evaluate valid polynomial f(x)=c"""
        polynomial_ok = auc.Polynomial({0:5})
        assert polynomial_ok.evaluate(3) == 5
        assert str(polynomial_ok) == "f(x)=5"

    def test_frac_ok(self):
        """correctly evaluate valid polynomial with fraction"""
        polynomial_ok = auc.Polynomial({1.5:1})
        assert polynomial_ok.evaluate(0) == 0
        assert polynomial_ok.evaluate(2) == 2 * math.sqrt(2)

    def test_fraction_reject(self):
        """reject negative input with fractional exponents"""
        with self.assertRaises(ValueError):
            polynomial_reject_fraction = auc.Polynomial({2.5:1})
            polynomial_reject_fraction.evaluate(-2)

    def test_negative_exp_reject(self):
        """reject negative exponents"""
        with self.assertRaises(ValueError):
            auc.Polynomial({-2:1})

    def test_negative_exp_frac_reject(self):
        """reject negative fractional exponents"""
        with self.assertRaises(ValueError):
            auc.Polynomial({-2.5: 1})


class ParseArgumentsTest(unittest.TestCase):
    """Test class for parsing command line arguments """
    def test_ok(self):
        """basic successful argument test"""
        parsed_params = auc.parse_arguments(["-p", "{3:2}", "-s", ".2", "-a",
                                             "simpson", "-l", "-2", "-u", "1.5"])
        assert parsed_params.bounds.step_size == .2
        assert parsed_params.bounds.lower_bound == -2
        assert parsed_params.bounds.upper_bound == 1.5
        assert parsed_params.polynomial.coefficient_dict[3] == 2
        assert parsed_params.algorithm.__name__ == "simpson"

    def test_invalid_algorithm(self):
        """reject incorrect algorithm name"""
        parsed_params = auc.parse_arguments(["-p", "{3:2}", "-s", ".2", "-a", "simpsonx"])
        assert parsed_params is None

    def test_negative_exponent(self):
        """reject negative exponents"""
        parsed_params = auc.parse_arguments(["-p", "{-3:2}", "-s", ".2", "-a", "simpson"])
        assert parsed_params is None

    def test_fractional_exponent_negative_value(self):
        """reject fractional exponents with negative bounds"""
        parsed_params = auc.parse_arguments(["-p", "{1.5:2}", "-s", ".2",
                                             "-l", "-5", "-a", "simpson"])
        assert parsed_params is None

    def test_invalid_step(self):
        """reject step size <=0"""
        parsed_params = auc.parse_arguments(["-p", "{1.5:2}", "-s", "-1"])
        assert parsed_params is None

    def test_invalid_bounds(self):
        """reject lower bound > upper bound"""
        parsed_params = auc.parse_arguments(["-p", "{1.5:2}", "-l", "1", "-u", "0"])
        assert parsed_params is None

    def test_invalid_polynomial_set(self):
        """reject invalid polynomial string"""
        parsed_params = auc.parse_arguments(["-p", "{3-1}", "-s", ".2", "-a", "simpson"])
        assert parsed_params is None

    def test_invalid_polynomial_numeric_s(self):
        """reject invalid polynomial string"""
        parsed_params = auc.parse_arguments(["-p", "{3a:2}"])
        assert parsed_params is None

    def test_invalid_polynomial_numeric_v(self):
        """reject invalid polynomial string"""
        parsed_params = auc.parse_arguments(["-p", "{a}"])
        assert parsed_params is None

    def test_invalid_option(self):
        """reject invalid option"""
        parsed_params = auc.parse_arguments(["-z", "3"])
        assert parsed_params is None

    def test_invalid_number(self):
        """reject invalid numerical argument"""
        parsed_params = auc.parse_arguments(["-l", "x3"])
        assert parsed_params is None

    def test_help(self):
        """test help string"""
        try:
            auc.parse_arguments(["-h"])
        except SystemExit:
            return


class AreaTest(unittest.TestCase):
    """Test class for parsing command line arguments """
    def test_simple_area_1(self):
        """area test 1"""
        bounds = auc.Bounds(0, 10, .1)
        polynomial = auc.Polynomial({1:1}) # f(x) = x
        algorithm = auc.get_algorithm("trapezoid")
        area = auc.area_under_curve(polynomial, bounds, algorithm)
        self.assertAlmostEqual(area, 50)

    def test_simple_area_2(self):
        """area test 2"""
        bounds = auc.Bounds(0, 10, .1)
        polynomial = auc.Polynomial({2:1}) # f(x) = x^2
        algorithm = auc.get_algorithm("simpson")
        area = auc.area_under_curve(polynomial, bounds, algorithm)
        self.assertAlmostEqual(area, 1000/3)

    def test_simple_area_3(self):
        """area test 3"""
        bounds = auc.Bounds(-5, 5, .1)
        polynomial = auc.Polynomial({3:1}) # f(x) = x^3
        algorithm = auc.get_algorithm("midpoint")
        area = auc.area_under_curve(polynomial, bounds, algorithm)
        self.assertAlmostEqual(area, 0)

class EntryPointTest(unittest.TestCase):
    """Test main entrypoint"""
    def test_entrypoint_ok(self):
        """test valid command line"""
        auc.area_under_curve_argv(["area_under_curve.py", "-p", "{3:1}", "-l", "0",
                                   "-u", "10", "-s", ".1", "-a", "simpson"])

    def test_entrypoint_invalid(self):
        """reject invalid command line"""
        with self.assertRaises(SystemExit):
            auc.area_under_curve_argv(["area_under_curve.py", "-p", "{a}"])

if __name__ == "__main__":
    unittest.main()
