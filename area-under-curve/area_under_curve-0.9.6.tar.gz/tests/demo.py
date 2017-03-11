#!python3
"""Simple test with logging"""
import sys

sys.path.insert(0, '../area_under_curve/')

import area_under_curve as auc
auc.LOGGING = True

def main():
    """Simple demo"""
    auc.log("Try out some sample polynomials, bounds, step sizes, and algorithms.")
    trapezoid = auc.get_algorithm("trapezoid")
    midpoint = auc.get_algorithm("midpoint")
    simpson = auc.get_algorithm("simpson")
    bounds_simple_1 = auc.Bounds(0, 10, .1)
    bounds_simple_2 = auc.Bounds(0, 10, 1)
    bounds_symmetric_1 = auc.Bounds(-5, 5, .1)
    polynomial_simple_cubic = auc.Polynomial({3:1})
    polynomial_simple_fractional = auc.Polynomial({.5:1})

    auc.log("-Demo 1")
    auc.log("Area={}".format(auc.area_under_curve(
        polynomial_simple_cubic, bounds_simple_1, midpoint)))

    auc.log("\n-Demo 2 -- larger step size, lower accuracy")
    auc.log("Area={}".format(auc.area_under_curve(
        polynomial_simple_cubic, bounds_simple_2, midpoint)))

    auc.log("\n-Demo 3 -- symmetric bounds and a symmetric function (net area close to zero)")
    auc.log("Area={}".format(auc.area_under_curve(
        polynomial_simple_cubic, bounds_symmetric_1, simpson)))

    auc.log("\n-Demo 4 -- fractional exponents")
    # integral of f(x)=x^.5 is (x^1.5)1.5 + sc, or (10*sqrt(10))/1.5 with these bounds
    auc.log("Area={}".format(auc.area_under_curve(
        polynomial_simple_fractional, bounds_simple_1, trapezoid)))


if __name__ == "__main__":
    main()
