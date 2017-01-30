"""
    effectus.exceptions
    ~~~~~~~~~~~~~~~~~~~

    Exceptions and checking functions to raise them.

    :copyright: (c) 2017 by Benjamin Weber
    :license: MIT, see LICENSE for more details.
"""

from click.exceptions import UsageError

from effectus.helpers import unfold_values


class StringFound(ValueError):
    """Raised if a string is found where only values are allowed."""


class InvalidFrequencyCount(ValueError):
    """Raised if number of values does not equal that of frequencies."""


class InvalidFrequencyValue(ValueError):
    """Raised if frequency is not None or not an integer."""


class MixedPrefixes(ValueError):
    """Raised if values contain negative and positive ones."""


class ExcelNotOpen(OSError):
    """Raised if Excel is not open."""


class ExcelNoValuesSelected(OSError):
    """Raised if no selection has been made in Excel."""


class InvalidLimit(ValueError):
    """Raised if limit is not between 0 and 1 (including)."""


def check_vafreqs(vafreqs):
    """Checks whether values to be valid.

    Args:
        vafreqs(List[(float, int)]): A tuple of value and frequency.

    Raises:
        StringFound: No value must be a string.
        InvalidFrequencyCount: Each value must have a frequency.
        InvalidFrequencyValue: Any frequency can only be of
          integer type.
        MixedPrefixes: The observations must be negative or positive
          only. You may want to shift the values that in turn the
          lowest value becomes zero.
    """

    if not no_string(vafreqs):
        raise StringFound
    elif not same_frequency_count(vafreqs):
        raise InvalidFrequencyCount
    elif not frequency_is_integer(vafreqs):
        raise InvalidFrequencyValue
    elif not matching_prefixes(vafreqs):
        raise MixedPrefixes


def check_and_unfold_vafreqs(vafreqs):
    """Checks und unfolds vafreqs.

    Args:
        vafreqs(List[(float, int)]): A tuple of value and frequency.

    Returns:
        List[float]: List of values.

    Raises:
        UsageError
    """
    try:
        check_vafreqs(vafreqs)
    except StringFound:
        raise UsageError('no value must be a string - '
                         'but at least one does.')
    except MixedPrefixes:
        raise UsageError('observations may be either '
                         'negative or positive only.')
    except InvalidFrequencyCount:
        raise UsageError('each value must have a frequency.')
    except InvalidFrequencyValue:
        raise UsageError('each frequency has to be '
                         'a positive integer.')

    effect_values = unfold_values(vafreqs)
    if len(effect_values) == 0:
        raise UsageError('Could not extract any value. '
                         'Check file. If your column '
                         'separator is not comma (,), specify '
                         'it with `--delimiter` option.')
    return effect_values


def no_string(vafreqs):
    """Returns False if a string is in vafreq."""
    for vafreq in vafreqs:
        if isinstance(vafreq, tuple):
            value, frequency = vafreq
            if (isinstance(value, str) or
                    isinstance(frequency, str)):
                return False
        else:
            value = vafreq
            if isinstance(value, str):
                return False
    return True


def same_frequency_count(vafreqs):
    """Checks whether each value has a frequency.

    Args:
        vafreqs(List[(float, int)]): A tuple of value and frequency.

    Returns:
        bool: True if each value has a frequency, otherwise False.

    Examples:
        >>> same_frequency_count([(1, 1), (1, 2)])
        True

        >>> same_frequency_count([(1, 1), (1, None)])
        False
    """
    for _, frequency in vafreqs:
        if frequency is None:
            return False
    return True


def frequency_is_integer(vafreqs):
    """Checks whether each frequency is integer.

    Args:
        vafreqs(List[(float, int]): A tuple of value and frequency.

    Returns:
        bool: True if all frequencies are integer, otherwise False.

    Examples:
        >>> frequency_is_integer([(1, 1), (2, 1)])
        True

        >>> frequency_is_integer([(1, 1), (2, 1.1)])
        False
    """
    for _, frequency in vafreqs:
        if frequency % 1 != 0:
            return False
    return True


def matching_prefixes(vafreqs):
    """Checks all values to be either positive or negative only (0 is neutral).

    Args:
        vafreqs (List[float]): A list of numbers.

    Returns:
        bool: True if all values are positive or negative, otherwise False.

    Examples:
        >>> matching_prefixes([0, 1, 2, 3])
        True

        >>> matching_prefixes([0, -1, -2, -3])
        True

        >>> matching_prefixes([0, -1, 2, -3])
        False
    """
    values = [value for value, _ in vafreqs]
    total_count = len(values)
    minus = len(list(filter(lambda value: value >= 0, values)))
    plus = len(list(filter(lambda value: value <= 0, values)))
    return total_count == minus or total_count == plus


def valid_limit(limit):
    """Checks limit to be between 0 and 1."""
    return limit >= 0 and limit <= 1


def check_valid_limit(limit):
    """Calls valid_limit and raises InvalidLimit if False."""
    if valid_limit(limit):
        return True
    else:
        raise InvalidLimit
