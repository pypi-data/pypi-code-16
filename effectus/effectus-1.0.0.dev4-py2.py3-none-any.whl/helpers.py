"""
    effectus.helpers
    ~~~~~~~~~~~~~~~~

    The building blocks for the core functions.

    :copyright: (c) 2017 by Benjamin Weber
    :license: MIT, see LICENSE for more details.
"""

from math import gcd
from collections import Counter

# pragma pylint: disable=no-name-in-module
from quicktions import Fraction
# pragma pylint: enable=no-name-in-module


def frac_gcd(frac1, frac2):
    """Determines greatest common fraction of two fractions.

    Args:
        frac1 (Fraction): Fraction.
        frac2 (Fraction): Fraction.

    Returns:
        Triplet with greatest common fraction, multiplier for frac1 and frac2.

    Example:
        >>> frac_gcd(Fraction(1, 55), Fraction(3, 110))
        (Fraction(1, 110), 2, 3)
    """
    the_gcd = Fraction(1, gcd(frac1.denominator, frac2.denominator))
    frac1_cd = frac1/the_gcd
    frac2_cd = frac2/the_gcd

    if frac1_cd.denominator != 1:
        the_gcd = the_gcd/frac1_cd.denominator
        new_frac1_cd = frac1_cd.denominator*frac1_cd
        new_frac2_cd = frac1_cd.denominator*frac2_cd

    if frac2_cd.denominator != 1:
        the_gcd = the_gcd/frac2_cd.denominator
        new_frac1_cd = frac2_cd.denominator*frac1_cd
        new_frac2_cd = frac2_cd.denominator*frac2_cd

    if frac1_cd.denominator == 1 and frac2_cd.denominator == 1:
        new_frac1_cd = frac1_cd
        new_frac2_cd = frac2_cd

    return (the_gcd, int(new_frac1_cd), int(new_frac2_cd))


def get_gcd(major_relations):
    """Determines relation with greatest common fraction.

    Args:
        major_relations(List[Tuple]): A list of tuples of
          cause-effect mappings, for example::

            [(Fraction(2, 3), Fraction(23, 33)),
             (Fraction(5, 6), Fraction(28, 33))]

    Returns:
        Cause-effect relationship with greatest common
        fraction as tuple.

    Example:
        >>> get_gcd([(Fraction(2, 3), Fraction(23, 33)),
        ...          (Fraction(5, 6), Fraction(28, 33))])

        (Fraction(2, 3), Fraction(23, 33))
    """
    frac_gcds = []
    for frac1, frac2 in major_relations:
        frac_gcds.append(frac_gcd(frac1, frac2))

    # det minimum denominator
    frac_gcds_only = [the_gcd for the_gcd, _, _ in frac_gcds]
    if len(frac_gcds_only) > 0:
        peak_gcd = max(frac_gcds_only)
    else:
        return

    for ordinal, (the_gcd, frac1, frac2) in enumerate(frac_gcds, 0):
        if the_gcd == peak_gcd:
            peak_ordinal = ordinal

    return major_relations[peak_ordinal]


def sort_effects(effect_values):
    """Sorts values descending.

    Args:
        effect_values (List[number]): Effects as list of numbers.

    Returns:
        List[number]: Sorted list of effect values with decreasing value.

    Example:
        >>> sort_effects([65, 27, 15, 621, 109, 30, 45, 789, 9, 12])
        [789, 621, 109, 65, 45, 30, 27, 15, 12, 9]
    """
    sorted_effects = list(effect_values)
    sorted_effects.sort()
    sorted_effects.reverse()
    return sorted_effects


def find_nearest(num, number_list):
    """Which number in number_list is nearest to number?

    Args:
        num (number): Value to find nearest value for in ``number_list``.
        number_list (List[Fraction]): Predefined list of 0 < Fractions < 1.

    Returns:
        float: Nearest value in `number_list` for `num`.

    Example:
        >>> find_nearest(0.15, [Fraction(1, 5), Fraction(1, 6)])
        Fraction(1, 6)
    """
    prev = None
    prev_delta = 0
    for ordinal, compare_to in enumerate(number_list):
        delta = abs(num-compare_to)
        if not prev or delta < prev_delta:
            prev_delta = delta
            prev = ordinal
    return number_list[prev]


def decimal_range(lower, upper, decimal_places):
    """Returns list of decimals in the range of lower and upper.
    The step between two neighbouring is 1/10**decimal_places.
    """
    result = []
    # move numbers to the left of the decimal point
    working_step = int(Fraction(10**decimal_places, 10))
    # 10**2 == 100
    # Fraction(100, 1)
    working_lower = int(Fraction.from_float(lower) * 10**decimal_places)
    working_upper = int(Fraction.from_float(upper) * 10**decimal_places)
    # use working_upper + working_step as real_upper bound as range
    # otherwise would not include working_upper
    for ordinal in range(working_lower,
                         working_upper+working_step, working_step):
        # move numbers back to the right of the decimal point
        result.append(Fraction(ordinal, 10**decimal_places))
    return result


def make_relations(effect_values):
    """Creates list of tuples (cumulative_causes, cumulative_effects)
    from effects.

    Args:
        effect_values (List[number]): Effects as list of numbers.

    Returns:
        A list of tuples with cause-effect mappings, for
        example::

        [(Fraction(1, 10), Fraction(263, 574)), ...]

    Example:
        >>> make_relations([789, 621, 109, 65, 45, 30, 27, 15, 12, 9])
        [(Fraction(1, 10), Fraction(263, 574)),
         (Fraction(1, 5), Fraction(235, 287)),
         (Fraction(3, 10), Fraction(217, 246)),
         (Fraction(2, 5), Fraction(264, 287)),
         (Fraction(1, 2), Fraction(543, 574)),
         (Fraction(3, 5), Fraction(79, 82)),
         (Fraction(7, 10), Fraction(281, 287)),
         (Fraction(4, 5), Fraction(81, 82)),
         (Fraction(9, 10), Fraction(571, 574)),
         (Fraction(1, 1), Fraction(1, 1))]
    """
    relations = []
    count = len(effect_values)
    total = sum(effect_values)
    runner = 0
    for ordinal, value in enumerate(sort_effects(effect_values), 1):
        runner += value
        relations.append((Fraction(ordinal, count),
                          Fraction(Fraction.from_float(runner),
                                   Fraction.from_float(total))))
    return relations


def get_majors(relations):
    """Gets only causes <= 0.52 and effects >= 0.48.

    Args:
        relations: A list of tuples with cause-effect mappings. This is the
                  output of ``make_relations``.

    Returns:
        A list of tuples with cause-effect mappings, for example::

        [(0.52, 0.48)]

    Example:
        >>> get_majors([(0.52, 0.48), (0.52, 0.47), (0.53, 0.48)])
        [(0.52, 0.48)]
    """
    result = []
    for given_causes, given_effects in relations:
            # skip if causes > 0.5 or effects < than 0.5
        if (given_causes - Fraction(2, 100) <= Fraction(1, 2) and
                given_effects + Fraction(2, 100) >= Fraction(1, 2)):
            result.append((given_causes, given_effects))
    return result


def get_relevant(major_relations, causes_list=None, effects_list=None):
    """Returns only relevant variations of causes and effects as tuples.

    Args:
        relations: A list of tuples with cause-effect mappings. This is the
          output of ``make_relations``.
        causes_list: A list of causes that are relevant. A cause may be any
            value between 0 and 1.
        effects_list: A list of effects that are relevant. An effect may be any
            value between 0 and 1.

    Returns:
        A list of tuples with cause-effect mappings with total_delta and
        greatest common decimal denominator.

    Example:
        >>> relations = make_relations([789, 621, 109, 65, 45, 30,
        ...                             27, 15, 12, 9])
        >>> major_relations = get_majors(relations)
        >>> get_relevant(major_relations)
        [(Fraction(1, 5), Fraction(4, 5), Fraction(27, 1175),
          Fraction(1, 5)), (Fraction(3, 10), Fraction(9, 10),
          Fraction(22, 1085), Fraction(1, 10)), (Fraction(2, 5),
          Fraction(9, 10), Fraction(19, 880), Fraction(1, 10)),
         (Fraction(1, 2), Fraction(9, 10), Fraction(44, 905),
          Fraction(1, 10))]
    """
    causes_list = causes_list or [Fraction(1, 100), Fraction(5, 100),
                                  Fraction(1, 10), Fraction(3, 10),
                                  Fraction(1, 5), Fraction(2, 5),
                                  Fraction(3, 5),
                                  Fraction(1, 4),
                                  Fraction(1, 3),
                                  Fraction(1, 2)]
    effects_list = effects_list or [Fraction(95, 100),
                                    Fraction(9, 10),
                                    Fraction(3, 5), Fraction(4, 5),
                                    Fraction(2, 3),
                                    Fraction(1, 2)]
    result = list()
    for given_causes, given_effects in major_relations:
        nearest_causes = find_nearest(given_causes, causes_list)
        nearest_effects = find_nearest(given_effects, effects_list)
        delta_causes = abs(nearest_causes - given_causes) / given_causes
        delta_effects = abs(nearest_effects - given_effects) / given_effects
        total_delta = delta_causes + delta_effects
        if total_delta <= 0.05:
            the_gcd, _, _ = frac_gcd(nearest_causes, nearest_effects)
            result.append((nearest_causes,
                           nearest_effects,
                           total_delta,
                           the_gcd))
    return result


def pick_best(relevant_relations):
    """Picks the single relation with the highest power.

    Args:
        relevant_relations: A list of relevant cause-effect
          relations that is tuple (causes, effects, total_delta,
          gcd). This is the output from ``get_relevant``.

    Returns:
        A dict with the most relevant cause-effect relationship.

    Example:
        >>> relations = make_relations([789, 621, 109, 65, 45, 30,
        ...                             27, 15, 12, 9])
        >>> relevant = get_relevant(relations)
        >>> pick_best(relevant)
        {'causes': Fraction(1, 5),
         'effects': Fraction(4, 5),
         'gcd': Fraction(1, 5),
         'variability': 0.02297872340425532}
    """
    prev_power = None
    pick = {}
    for causes, effects, delta, the_gcd in relevant_relations:
        if causes + effects == 1:
            power = effects / causes * 2
        else:
            power = effects / causes
        if prev_power is None or power > prev_power:
            pick = {'causes': causes,
                    'effects': effects,
                    'gcd': the_gcd,
                    'variability': float(delta)}
        prev_power = power
    if pick != {}:
        return pick


def format_summary(summary, precision=3):
    """Extends summary dict by ``pareto`` and ``ratio``, fracifies or rounds it.

    Args:
        summary (dict): A summary created by ``pick_best`` or ``get_gcd``.
        precision (int): Digits to round to.

    Returns:
        A tuple with (causes, effects) in fractional notation if both
        denominators are less or equal 100, otherwise in decimal notation.
    """
    if (summary['causes'].denominator > 100 or
            summary['effects'].denominator > 100):
        causes = round(float(summary['causes']), precision)
        effects = round(float(summary['effects']), precision)
    else:
        causes = '{}/{}'.format(summary['causes'].numerator,
                                summary['causes'].denominator)
        effects = '{}/{}'.format(summary['effects'].numerator,
                                 summary['effects'].denominator)
    return causes, effects


# Value Handling

def reduce_values(values):
    """Reduces a list of values into a value-frequency mapping.

    Args:
        values (List[number]): Effects as list of numbers.

    Returns:
        A list of tuples of like [(value, frequency), ...].

    Example:
        >>> reduce_values([1,1,1,3,2])
        [(1, 3), (3, 2)]
    """
    vafreqs = Counter()

    for value in values:
        vafreqs[value] += 1

    outlist = []
    for value, freq in vafreqs.items():
        outlist.append('{},{}'.format(value, freq))
    return outlist


def write_reduced_values(values, filename):
    """Writes value-frequency mappings to file.

    Args:
        values (List[number]): Effects as list of numbers.
        filename: File path to write to.

    Return:
        Nothing. The value-frequency mappings are written
        separated by comma line-wise to the given filename.

    Example:
        >>> write_reduced_values([1,1,1,1,3,3])
    """
    outlist = reduce_values(values)
    with open(filename, 'w') as target:
        target.write('\n'.join(outlist))


def get_values(csv_reader, observations_col=1, frequency_col=2):
    """Gets values from csv file.

    Args:
        csv_reader:
        observations_col (int): Column number of observations (default: 1).
        frequency_col (int): Column number of frequency (default: 2).
          if < 0 or csv file has only one column, values will only
          be considered.

    Returns:
        A list of observation-frequency tuples
        like::

        [(23.3, 1), (80.1, 3), (99.3, 2)]
    """
    result = []
    for row in csv_reader:
        try:
            observation = float(row[observations_col-1])
            frequency = 1
        except (ValueError, IndexError):
            continue
        if len(row) > 1:
            try:
                if frequency_col < 0:
                    frequency = 1
                else:
                    frequency = int(row[frequency_col-1])
            except (ValueError, IndexError):
                raise ValueError
        else:
            frequency = 1
        result.append((observation, frequency))
    return result


def unfold_values(values):
    """Unfolds list of observation-frequency mappings.

    Args:
        values (Tuple[number, int]): observation-frequency mapping.

    Returns:
        List[number]: List of values.

    Example:
        >>> unfold_values([(1, 3), (2, 1), (3, 1)])
        [1, 1, 1, 2, 3]
    """
    result = []
    for observation, frequency in values:
        result += [observation] * frequency
    return result
