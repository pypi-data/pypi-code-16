#!python3
"""Find approximate area under curve:  Supports simpson, trapezoid, and
midpoint algorithms,  n-degree single variable polynomials, and variable step size
"""
import ast
import collections
import getopt
import math
import sys
import numpy

LOGGING = True # Typically set to false when not using interactively

USAGE = """ -p|--poly {DegreeN1:CoefficientM1, DegreeN2:CoefficientM2, ...}
-l|--lower <lower_bound> -u|--upper <upper_bound> -s|--step <step> 
-a|--algorithm <simpson | trapezoid | midpoint>
  defaults: step_size:1, lower_bound:0, upper_bound:10, algorithm:trapezoid

e.g. To evaluate the area of y=x^2 + 2x -2 from [1-50] with .1 width sums and the midpoint algorithm:
 python area_under_curve.py --poly "{2:1, 1:2, 0:-2}" --lower 1 --upper 50 --step .1 --algorithm midpoint
"""

FULL_USAGE = USAGE

Parameters = collections.namedtuple("Parameters", ["polynomial", "bounds", "algorithm"])

class Bounds:
    """Range of values class"""
    def __init__(self, lower_bound, upper_bound, step_size):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.step_size = step_size
        if step_size <= 0:
            raise ValueError("step size must be > 0")
        if upper_bound <= lower_bound:
            raise ValueError("invalid bounds")
        self.full_range = numpy.arange(lower_bound, upper_bound + step_size, step_size).tolist()

    def __str__(self):
        return "Bounds: [{} - {}], step_size: {}".format(
            self.lower_bound, self.upper_bound, self.step_size)


class Polynomial:
    """Single variable polynomial class supporting n degrees"""
    def __init__(self, coefficient_dict):
        """ The coefficient dict keys are the term orders, and the values are the coefficients
            e.g
            f(x) = 3x^2 would be expressed as {2:3}
            f(x) = 9x^5 + 3 would be {5:9, 0:3}
        """
        self.fractional_exponents = False

        self.coefficient_dict = coefficient_dict
        if any_negative(coefficient_dict.keys()):
            raise ValueError("Only positive exponents supported")

        if any_non_int_numbers(coefficient_dict.keys()):
            self.fractional_exponents = True

    def format_term(self, degree, value):
        """string format a single term"""
        value_formatted = str(value)
        if value == 1:
            value_formatted = ""
        if value == 0:
            return
        if degree == 0:
            return str(value)
        else:
            if degree == 1:
                return "{}x".format(value_formatted)
            else:
                return "{}x^{}".format(value_formatted, degree)

    def __str__(self):
        """string format the entire polynomial"""
        terms = []
        degrees = list(self.coefficient_dict.keys())
        degrees.sort()
        degrees.reverse()
        for degree in degrees:
            term_formatted = (self.format_term(degree, self.coefficient_dict[degree]))
            if term_formatted:
                terms.append(term_formatted)
        if not terms:
            return "f(x)=0"
        return "f(x)={}".format(" + ".join(terms))

    def evaluate(self, value):
        """Evaluate the polynomial at a given value"""
        total = 0
        for degree in self.coefficient_dict:
            coefficient = self.coefficient_dict[degree]
            if self.fractional_exponents and value < 0:
                raise ValueError("Fractional exponents not supported for negative inputs.")
            current_term = math.pow(value, degree)* coefficient
            total += current_term
        return total

def parse_polynomial_coefficients(dict_literal):
    """Try to parse string into dictionary, return None on failure"""
    coefficient_dict = {}
    try:  # Need more validation here!
        coefficient_dict = ast.literal_eval(dict_literal)
    except SyntaxError as errs:
        log("Syntax Error parsing polynomial args: {} {}".format(dict_literal, str(errs)))
    except ValueError as errv:
        log("Value Error parsing polynomial args: {} {}".format(dict_literal, str(errv)))
        return None
    if not isinstance(coefficient_dict, dict):
        log("Malformed dictionary: {}".format(coefficient_dict))
        return None
    else:
        return coefficient_dict


def log(string):
    """Simple logging"""
    if LOGGING:
        print(string)

def is_number(string):
    """Simple check to see if string is valid number"""
    try:
        float(string)
        return True
    except ValueError as err:
        log("Error: {} {}".format(string, str(err)))
        return False

def any_non_int_numbers(collection):
    """Returns true if any numbers in the collection are not integers"""
    return any(map(lambda n: not isinstance(n, int), collection))

def any_negative(collection):
    """Returns true if any numbers in the collection are < 0"""
    return any(map(lambda n: n < 0, collection))

def has_property(name):
    """Simple function property decorator"""
    def wrap(func):
        """Wrapper function"""
        setattr(func, name, True)
        return func
    return wrap

def parse_arguments(argv):
    """Parse command line arguments and return a parameters
    object with Bounds, Polynomial, and Algorithm
    """
    lower = 0
    upper = 10
    step_size = 1
    algorithm = "trapezoid"
    polynomial_coefficients = {}
    try:
        opts, args = getopt.getopt(argv, "hl:u:s:a:p:",
                                   ["lower=", "upper=", "step=",
                                    "algorithm=", "polynomial=", "help"])

        non_numerical_params = ["-a", "--algorithm", "-p", "--polynomial", "-h", "--help"]
        numerical_params = list(filter(lambda t: t[0] not in non_numerical_params, opts))
        if any(map(lambda n: not is_number(n[1]), numerical_params)):
            log("Error in numerical arguments.")
            return
    except getopt.GetoptError as err:
        log("Option error: {}".format(str(err)))
        return
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            log(FULL_USAGE)
            exit(0)
        elif opt in ("-l", "--lower"):
            lower = float(arg)
        elif opt in ("-u", "--upper"):
            upper = float(arg)
        elif opt in ("-s", "--step"):
            step_size = float(arg)
        elif opt in ("-a", "--algorithm"):
            algorithm = arg
        elif opt in ("-p", "--polynomial"):
            polynomial_coefficients = parse_polynomial_coefficients(arg)
        if step_size <= 0:
            log("step size must be > 0: {}".format(step_size))
            return
        if lower >= upper:
            log("invalid bounds: {} {}".format(lower, upper))
            return
        if (lower < 0 or upper < 0) and any_non_int_numbers(polynomial_coefficients.keys()):
            log("Fractional exponents not supported for negative values.")
            return
    algorithm_function = get_algorithm(algorithm)
    if not algorithm_function:
        log("Algorithm : {} not found!".format(algorithm))
        return
    if not polynomial_coefficients:
        log("Polynomial not specified or invalid")
        return
    if any_negative(polynomial_coefficients.keys()):
        log("Only positive exponents supported")
        return
    return get_parameters(polynomial_coefficients,
                          lower, upper, step_size, algorithm_function)

def get_parameters(polynomial_coefficients, lower, upper, step, algorithm):
    """Create parameters tuple from polynomial, bounds, and algorithm parameters"""
    bounds = Bounds(lower, upper, step)
    polynomial = Polynomial(polynomial_coefficients)
    return Parameters._make([polynomial, bounds, algorithm])

def get_algorithm(algorithm_name):
    """Get algorithm function by name by looking up in globals with the 'algorithm' attribute set"""
    if algorithm_name in globals():
        algorithm = globals()[algorithm_name]
        if "algorithm" in dir(algorithm):
            return globals()[algorithm_name]
    else:
        log("Algorithm {} not found or invalid!".format(algorithm_name))

@has_property("algorithm")
def midpoint(poly, lower, upper):
    """Calculate midpoint slice from two polynomial evaluations and step size"""
    value = poly.evaluate((upper+lower)/2)
    return (upper - lower) * value

@has_property("algorithm")
def trapezoid(poly, lower, upper):
    """Calculate trapezoid slice from two polynomial evaluations and step size"""
    lower_value = poly.evaluate(lower)
    upper_value = poly.evaluate(upper)
    return (upper - lower) * ((lower_value + upper_value)/2)

@has_property("algorithm")
def simpson(poly, lower, upper):
    """Calculate parabola (Simpson) slice from two polynomial evaluations and step size"""
    lower_value = poly.evaluate(lower)
    upper_value = poly.evaluate(upper)
    midpoint_value = poly.evaluate((lower+upper)/2)
    return ((upper - lower) / 6) * (lower_value + 4 * midpoint_value + upper_value)

def area_under_curve(poly, bounds, algorithm):
    """Finds the area under a polynomial between the specified bounds
    using a rectangle-sum (of width 1) approximation.
    """
    log(bounds)
    log(poly)
    log("Algorithm: {}".format(algorithm.__name__))
    range_upper_index = len(bounds.full_range) - 1
    total_area = 0
    for range_index, val in enumerate(bounds.full_range):
        # Can't calculate trapezoid with only lower bound value, so we're done summing.
        if range_index == range_upper_index:
            return total_area
        else:
            total_area += algorithm(poly, val, bounds.full_range[range_index + 1])


def area_under_curve_argv(args):
    """Command-line entrypoint"""
    parsed_parameters = parse_arguments(args[1:])
    if not parsed_parameters:
        log(FULL_USAGE)
        exit(2)
    area = area_under_curve(parsed_parameters.polynomial,
                            parsed_parameters.bounds, parsed_parameters.algorithm)
    log("Total Area ({}) = {}".format(parsed_parameters.algorithm.__name__, area))


if __name__ == '__main__':
    FULL_USAGE = '{}\nUsage: python {} {}'.format(__doc__, sys.argv[0], USAGE)
    area_under_curve_argv(sys.argv)
