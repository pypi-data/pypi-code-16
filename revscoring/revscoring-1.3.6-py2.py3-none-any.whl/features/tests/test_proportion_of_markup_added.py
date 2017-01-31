from nose.tools import eq_

from ..proportion_of_markup_added import proportion_of_markup_added


def test_proportion_of_markup_added():
    
    eq_(proportion_of_markup_added(1, 10), 1/10)
    eq_(proportion_of_markup_added(2, 10), 2/10)
    eq_(proportion_of_markup_added(1, 1), 1) # prevents divide by zero
