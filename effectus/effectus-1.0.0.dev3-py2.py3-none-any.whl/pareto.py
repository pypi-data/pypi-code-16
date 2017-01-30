"""
    effectus.pareto
    ~~~~~~~~~~~~~~~

    Functions to determine entropy for a series of numbers,
    the control limit of their total count and whether the
    entropy is less or equal the control limit. If that's
    the case, a pareto distribution is present.

    :copyright: (c) 2017 by Benjamin Weber
    :license: MIT, see LICENSE for more details.
"""

from math import log


def control_limit(count):
    """Determines control limit.

    Args:
        count (int): Number of elements to calculate control entropy for. This
            is len(effects).

    Returns:
        float: Control limit.

    Example:
        >>> control_limit(10)
        2.7709505944546686
    """
    factor = count / 5
    majority = 0.6 * log(0.6 / factor, 2)
    minority = 0.4 * log(0.4 / (4 * factor), 2)
    return -1 * majority - minority


def entropy(effect_values):
    """Determines entropy for effects.

    Args:
        effect_values (List[number]): Effects as list of numbers.

    Returns:
        float: Entropy of effects.

    Example:
        >>> entropy([789, 621, 109, 65, 45, 30, 27, 15, 12, 9])
        1.9593816735406657
    """
    acc = 0

    # check observations to be positive or negative only
    negatives = len(list(filter(lambda x: x < 0, effect_values)))
    positives = len(list(filter(lambda x: x > 0, effect_values)))
    if negatives > 0 and positives > 0:
        raise ValueError("You may use positive OR negative "
                         "values only. Don't mix them ")

    sumv = sum(effect_values)
    for effect_value in effect_values:
        if effect_value != 0:
            share = effect_value / sumv
            subtrahend = share * log(share, 2)
            acc = acc - subtrahend
    return acc


def ratio(effect_values, precision=3):
    """Determines ratio of entropy versus control limit.

    Args:
        effect_values (List[number]): Effects as list of numbers.

    Returns:
        float: Ratio of entropy versus control limit. If it is 1 or
        less (entropy <= control_limit), a pareto distribution is
        present.

    Example:
        >>> ratio([789, 621, 109, 65, 45, 30, 27, 15, 12, 9])
        0.707
    """
    return(round(entropy(effect_values)/control_limit(len(effect_values)),
                 precision))


def pareto(effect_values):
    """Determines whether a pareto distribution is present.

    Is a pareto distribution present for `effects`?

    Args:
        effect_values (List[number]): Effects as list of numbers.

    Returns:
        bool: True if pareto distribution present, False otherwise.

    Example:
        >>> pareto([789, 621, 109, 65, 45, 30, 27, 15, 12, 9])
        True
    """
    return ratio(effect_values) <= 1
