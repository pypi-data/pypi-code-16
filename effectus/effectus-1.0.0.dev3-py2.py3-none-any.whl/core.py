"""
    effectus.core
    ~~~~~~~~~~~~~

    Main functions to determine if and which pareto distribution
    is present.

    :copyright: (c) 2017 by Benjamin Weber
    :license: MIT, see LICENSE for more details.
"""

# pragma pylint: disable=no-name-in-module
from quicktions import Fraction
# pragma pylint: enable=no-name-in-module

from effectus.helpers import (sort_effects, make_relations,
                              get_majors, get_relevant,
                              pick_best, get_gcd, format_summary)


def make_summary(effect_values, fracs=True):
    """Creates summary for cause-effect relationship.

    Args:
        effect_values (List[number]): Effects as list of numbers.
        fracs (Optional[bool]): True for decimal output, False for
          Fraction.

    Returns:
        A dict summarizing the cause-effect relationship.

    Example:
        >>> make_summary([789, 621, 109, 65, 45, 30, 27, 15, 12, 9])
        {'causes': '1/5',
         'effects': '4/5',
         'pareto': True,
         'ratio': 0.7071153406566882,
         'variability': 0.02}
    """
    relations = make_relations(effect_values)
    major_relations = get_majors(relations)
    relevant = get_relevant(major_relations)
    summary = pick_best(relevant)
    if not summary:
        summary = {'variability': 0.0}
        ggcd = get_gcd(major_relations)
        if ggcd:
            summary['causes'], summary['effects'] = ggcd
    if summary != {'variability': 0.0}:
        return format_summary(summary, effect_values, fracs)


def attain_effects(effect_values,
                   required_effects=Fraction(8, 10), precision=3):
    """Determines causes for specified ratio of effects.

    How many causes are at least required for `required_effects`?

    Args:
        effect_values (List[number]): Effects as list of numbers.
        required_effects (float): Effect ratio to attain between 0 and 1.
        precision (float): Number of decimals to round to.

    Returns:
        float: Minimum ratio of causes required to attain specified
        share of `required_effects`.

    Example:
        >>> attain_effects([789, 621, 109, 65, 45, 30, 27, 15, 12, 9])
        0.2
    """
    relations = make_relations(effect_values)
    for ordinal, relation in enumerate(relations):
        _, effects = relation
        if round(effects, precision) >= required_effects:
            return round(float(relations[ordinal][0]), precision)


def attain_causes(effect_values, required_causes=Fraction(1, 5), precision=3):
    """Determines causes for specified ratio of effects.

    How many effects are at least effected for `required_causes`?

    Args:
        effect_values (List[number]): Effects as list of numbers.
        required_causes (float): Causes ratio to attain, between 0 and 1.
        precision (float): Number of decimals to round to.

    Returns:
        float: Minimum ratio of effects required to attain specified
        share of `required_causes`.

    Example:
        >>> attain_causes([789, 621, 109, 65, 45, 30, 27, 15, 12, 9])
        0.882
    """
    relations = make_relations(effect_values)
    for ordinal, relation in enumerate(relations):
        causes, _ = relation
        if round(causes, precision) >= required_causes:
            return round(float(relations[ordinal][1]), precision)


def separate_causes(effect_values, required_causes, precision=3):
    """Determines threshold value that selects `required_causes` ratio.

    Which value must an effect be or be greater to belong
    to `required_causes`?

    Args:
        effect_values (List[number]): Effects as list of numbers.
        required_causes (float): Causes ratio to attain, between 0 and 1.
        precision (float): Number of decimals to round to.

    Returns:
        Tuple(a, b, c)
        `a` is value a effect must be at least to belong to `required_causes`.
        `c` is total count of occurences of that value.
        `b` is number of occurrence up to which selection must span (including)
        to attain `required_causes`.

    Examples:
        >>> separate_causes([789, 621, 109, 65, 45, 30, 27, 15, 12, 9], 0.6)
        (30, 1, 1)
    """
    sorted_effects = sort_effects(effect_values)
    effects_count = len(sorted_effects)
    effects = 0
    previous_effect_value = None
    equals_count = 0
    for ordinal, current_effect_value in enumerate(sorted_effects):
        effects += current_effect_value
        causes_cml_perc = Fraction((ordinal + 1), effects_count)
        if ordinal > 0:
            previous_effect_value = sorted_effects[ordinal-1]
            if previous_effect_value == current_effect_value:
                equals_count += 1
            else:
                equals_count = 0
        causes_cml_r = round(float(causes_cml_perc), precision)
        causes_cml_ge = causes_cml_r >= required_causes
        if causes_cml_ge:
            # http://stackoverflow.com/questions/12423614
            total_equal_count = sum(1 for x in sorted_effects
                                    if x == current_effect_value)
            return (current_effect_value, equals_count+1,
                    total_equal_count)


def separate_effects(effect_values, required_effects, precision=3):
    """Determines threshold value that selects `required_effects` ratio.

    Which value must an effect be or be greater to belong
    to `required_effects`?

    Args:
        effect_values (List[number]): Effects as list of numbers.
        required_effects (float): Causes ratio to attain, between 0 and 1.
        precision (float): Number of decimals to round to.

    Returns:
        Tuple of (a, b, c).
        `a` is value a effect must be at least to belong to
        `required_effects`.
        `c` is total count of occurences of that value.
        `b` is number of occurrence up to which selection must span (including)
        to attain `required_effects`.

    Examples:
        >>> separate_effects([789, 621, 109, 65, 45, 30, 27, 15, 12, 9], 0.6)
        (621, 1, 1)
    """
    sorted_effects = sort_effects(effect_values)
    effects = Fraction(0, 1)
    total_effects = sum(sorted_effects)
    equals_count = 0
    for ordinal, current_effect_value in enumerate(sorted_effects):
        effects += Fraction.from_float(current_effect_value)
        effects_cml_perc = Fraction(effects,
                                    Fraction.from_float(total_effects))
        if ordinal > 0:
            previous_effect_value = sorted_effects[ordinal-1]
            if previous_effect_value == current_effect_value:
                equals_count += 1
            else:
                equals_count = 0
        effects_cml_r = round(float(effects_cml_perc), precision)
        effects_cml_ge = effects_cml_r >= required_effects
        if effects_cml_ge:
            # http://stackoverflow.com/questions/12423614/local-variables-in-python-nested-functions
            total_equal_count = sum(1 for x in sorted_effects
                                    if x == current_effect_value)
            return (current_effect_value, equals_count+1,
                    total_equal_count)
