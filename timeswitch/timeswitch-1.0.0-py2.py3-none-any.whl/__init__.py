"""
'Timeswitch' is a library for expressing date/time ranges.
"""
from calendar import monthrange
from datetime import MINYEAR, MAXYEAR
from functools import reduce  # builtin removed in Python 3

from enum import Enum
from pyparsing import Word, nums, Literal, oneOf, infixNotation, opAssoc, ParseException, \
    ParseSyntaxException, ParserElement

# Enable element caching performance enhancement
# (works for grammars without global side effects during parsing, like ours)
ParserElement.enablePackrat()


class Period(Enum):
    # Constants for working with "ideal" calendar used for datetime
    # range comparisons.
    MINUTES = 1
    HOURS = MINUTES * 60
    DAYS = HOURS * 24
    WEEKS = DAYS * 7
    MONTHS = DAYS * 31  # All months have 31 days
    YEARS = MONTHS * 12
    FOREVER = (MAXYEAR - MINYEAR) * YEARS

    def __mul__(self, other):
        return self.value * other

    __rmul__ = __mul__

    def __sub__(self, other):
        return self.value - other


class End(Enum):
    # start_end enum passed to time_mask_to_ideal_calendar()
    START = 1
    END = 0


def _ideal_calendar_period(time_mask):
    """
    Given a time mask, after how many ideal calendar
    minutes would the mask repeat?

    :param time_mask: (year, month, day, nth weekday, weekday, time)
    :return: one of FOREVER, MONTHS, WEEKS or DAYS
    """
    if time_mask[0] is not None:
        return Period.FOREVER

    if time_mask[1] is not None:
        return Period.YEARS

    if time_mask[2] is not None or time_mask[3] is not None:
        return Period.MONTHS

    if time_mask[4] is not None:
        return Period.WEEKS

    return Period.DAYS


def _datetime_to_ideal_calendar(d, period):
    """
    Convert a real datetime to an integer value representing
    minutes on an "ideal" calendar, modulo the period
    of the time masks we will be compared against.

    :param d:       datetime
    :param period:  Number of ideal calendar minutes after
                    which the time_masks test_date is being compared
                    against will repeat
    :return:        integer ideal calendar minute representation
                    of test_date, modulo period
    """
    if period is Period.FOREVER:
        return (
            (d.year - 1) * Period.YEARS +  # year/month/day are 1-based
            (d.month - 1) * Period.MONTHS +
            (d.day - 1) * Period.DAYS +
            d.hour * Period.HOURS +     # hours/min are 0-based
            d.minute * Period.MINUTES)

    if period is Period.YEARS:
        return (
            (d.month - 1) * Period.MONTHS +
            (d.day - 1) * Period.DAYS +
            d.hour * Period.HOURS +
            d.minute * Period.MINUTES)

    if period is Period.MONTHS:
        return (
            (d.day - 1) * Period.DAYS +
            d.hour * Period.HOURS +
            d.minute * Period.MINUTES)

    if period is Period.WEEKS:
        return (
            (d.isoweekday() - 1) * Period.DAYS +  # Mon = 1, ..., Sun = 7
            d.hour * Period.HOURS +
            d.minute * Period.MINUTES)

    if period is Period.DAYS:
        return (
            d.hour * Period.HOURS +
            d.minute * Period.MINUTES)

    raise RuntimeError('Unexpected period value')


def time_mask_to_ideal_calendar(time_mask, d, period, start_end):
    """
    Convert a time mask to an ideal calendar minute count, modulo the
    period, taking into account the real datetime it will be
    compared against to resolve weekday alignment.

    The caller also specifies whether the minute count is to the start
    or end of the period specified by the mask. For instance if the mask
    refers to an entire year, passing START will return the ideal calendar
    minute count for midnight on January 1st, and passing END will return
    11:59 on December 31st.

    :param time_mask:   (year, month, day, nth weekday, weekday, time)
    :param d:           Real datetime we will be compared against
    :param period:      Number of ideal calendar minutes after
                        which the time_mask will repeat
    :param start_end    START or END of time_mask
    :return:            integer ideal calendar minute representation of
                        start or end of time-mask modulo period,
                        taking test_date into account for weekday-based comparisons
    """

    year, month, day, nth_weekday, weekday, time = time_mask

    # check if month and weekday specified, if yes derive day based on
    # real datetime test_date, and set weekday to None

    if (month is not None or nth_weekday is not None) and weekday is not None:

        # fill in a missing weekday ordinal
        if nth_weekday is None:
            nth_weekday = 1

        # find out weekday on 1st of the real month being checked
        month_start_weekday, _ = monthrange(d.year, d.month)

        # carefully calculate the day (1-31) of the nth specified weekday
        day = 7 + (weekday - month_start_weekday) + ((nth_weekday - 1) * 7)
        weekday = None

    # Default unspecified parts of time mask to minimum or maximum
    # possible values depending on start_end argument. Don't muck
    # around with nth weekday and weekday, we just fixed that above
    # for non-week periods, and we don't need to set min or max values
    # for weekday

    time_mask = _merge_time_masks(
        [(MINYEAR, 1, 1, None, None, 0)
         if start_end is End.START else
         (MAXYEAR, 12, 31, None, None, Period.DAYS - 1),  # DAYS - 1 = 23:59
         (year, month, day, nth_weekday, weekday, time)])

    year, month, day, nth_weekday, weekday, time = time_mask

    if period is Period.FOREVER:
        return (
            (year - 1) * Period.YEARS +  # year/month/day are 1-based
            (month - 1) * Period.MONTHS +
            (day - 1) * Period.DAYS +
            time * Period.MINUTES)

    if period is Period.YEARS:
        return (
            (month - 1) * Period.MONTHS +
            (day - 1) * Period.DAYS +
            time * Period.MINUTES)

    if period is Period.MONTHS:
        return (
            (day - 1) * Period.DAYS +
            time * Period.MINUTES)

    if period is Period.WEEKS:
        return (
            (weekday - 1) * Period.DAYS +
            time * Period.MINUTES)

    if period is Period.DAYS:
        return time * Period.MINUTES

    raise RuntimeError('Unexpected period value')


def _datetime_in_range(start, d, end):
    """
    Given optional start and end time masks, return true
    if the date falls within the range described by the
    masks.

    This is used by time_switch to construct the
    function it returns.
    """
    start_period = end_period = ideal_d = ideal_start = ideal_end = None

    if end is not None:
        end_period = _ideal_calendar_period(end)
        ideal_d = _datetime_to_ideal_calendar(d, end_period)
        ideal_end = time_mask_to_ideal_calendar(
            end, d, end_period, End.END)

    if start is not None:
        start_period = _ideal_calendar_period(start)
        ideal_d = _datetime_to_ideal_calendar(d, start_period)
        ideal_start = time_mask_to_ideal_calendar(
            start, d, start_period, End.START)

    if start is None and end is None:
        return True  # all dates and times are included

    elif start is not None and end is not None:

        if start_period != end_period:
            # with the compatibility check and shorthand
            # behaviour this should be impossible
            raise RuntimeError('Start and end repeat periods do not match')

        return ideal_start <= ideal_d <= ideal_end

    elif start is not None:
        return ideal_start <= ideal_d

    elif end is not None:
        return ideal_d <= ideal_end


def _time_masks_are_compatible(a, b):
    """
    For time masks to be used as the start and end of
    a range, they must specify the same rightmost element.
    For example the time masks in the ranges:

        2016 jan - 2016 mar
        2016 jan - mar
        jan 1 - 4
        10:40 - 10:50
        jun 1st mon 9:00 - 2nd fri 17:00

    are compatible, whereas:

        2016 - 2016 mar
        2016 Jan 20 10:40 - 2017 Jan

    are not. If the masks are compatible, unspecified components
    in the right mask will later be set to specified components
    in the left mask, so:

        2016 jan - mar

    is shorthand for:

        2016 jan - 2016 mar
    """
    for pair in reversed(list(zip(a, b))):
        if pair[0] is not None and pair[1] is not None:
            return True
        if not isinstance(pair[0], type(pair[1])):
            return False
    return True


def _merge_time_masks(masks):
    """
    Given an array of time mask tuples, create a new tuple
    from the non-None elements. For example:

        [
            (2016, None, None, None, None, None),
            (None, None, 7, None, None, None),
            (None, 10, None, None, None, 100)
        ]

    becomes:

        (2016, 10, 7, None, None, 100)

    If more than one corresponding tuple element is not None,
    use the last one (this is to support shorthand ranges in
    the range_from_to parsing action).
    """

    return tuple([
        next((value for value in
              reversed(csp_elements) if value is not None), None)
        for csp_elements in zip(*masks)])


class InvalidExpression(ValueError):
    def __init__(self, expression, caused_by):
        super(InvalidExpression, self).__init__(
            "Bad timeswitch expression {!r} - {}".format(expression, caused_by))
        self.expression = expression


def timeswitch(expression,
               months='jan feb mar apr may jun jul aug sep oct nov dec'.split(' '),
               weekdays='mon tue wed thu fri sat sun'.split(' '),
               ordinals='1st 2nd 3rd 4th 5th'.split(' ')):
    """
    Given a string expression describing a time range, return a function that
    when passed a datetime, returns true if that datetime is within the
    range described.

    In a pathetic nod to localisation the month, weekday and ordinal
    names can be overridden.

    :param expression: Expression describing a date/time range.
    :param months: List of locale-specific month names.
    :param weekdays: List of locale-specific names for the days of the week.
    :param ordinals: List of locale-specific ordinals, representing the 'n-th' day of the month.

    :return: Function which determines if the provided datetime matches the timeswitch expression.

    :type expression: str
    :type months: list[str]
    :type weekdays: list[str]
    :type ordinals: list[str]
    :rtype: function[datetime]

    :raises InvalidExpression: when the expression cannot be parsed.
    """

    month_lookup = \
        {code: index for index, code in enumerate(months)}

    weekday_lookup = \
        {code: index for index, code in enumerate(weekdays)}

    ordinal_lookup = \
        {code: index for index, code in enumerate(ordinals)}

    and_op = Literal('and').suppress()
    or_op = Literal('or').suppress()
    not_op = Literal('not').suppress()
    dash = Literal('-').suppress()

    # The following basic time grammar elements all generate tuples in the
    # following "time mask" format:
    #
    #   (year, month, day, nth weekday, weekday, hmin)
    #
    # This makes it easier to combine them later - we use them like a bit mask

    year = Word(nums)\
        .setParseAction(
            lambda t: (int(t[0]), None, None, None, None, None))\
        .addCondition(
            lambda t: MINYEAR <= int(t[0][0]) <= MAXYEAR,
            message="Year must be in range {}-{}".format(MINYEAR, MAXYEAR))

    month_num = Word(nums)\
        .setParseAction(
            lambda t: (None, int(t[0]), None, None, None, None))\
        .addCondition(
            lambda t: 1 <= int(t[0][1]) <= 12,
            message="Month must be in range 1-12")

    month = oneOf(months, True)\
        .setParseAction(
            lambda t: (None, month_lookup[t[0]] + 1, None, None, None, None))

    day = Word(nums)\
        .setParseAction(
            lambda t: (None, None, int(t[0]), None, None, None))\
        .addCondition(
            lambda t: 1 <= int(t[0][2]) <= 31,
            message="Day must be in range 1-31")

    ordinal = oneOf(ordinals, True)\
        .setParseAction(
            lambda t: (None, None, None, ordinal_lookup[t[0]] + 1, None, None))

    weekday = oneOf(weekdays, True)\
        .setParseAction(
            lambda t: (None, None, None, None, weekday_lookup[t[0]] + 1, None))

    hmin = \
        Word(nums).addCondition(
            lambda t: 0 <= int(t[0]) < 24,
            message='Hour must be in range 0-23') - \
        Literal(':').suppress() - \
        Word(nums).addCondition(
            lambda t: 0 <= int(t[0]) < 60,
            message='Minute must be in range 0-59')

    hmin.setParseAction(
        lambda t: (None, None, None, None, None, int(t[0]) * 60 + int(t[1])))

    # The following compound parser elements merge the above elements
    # into the same "time mask" tuples

    year_month_day_hmin = \
        year - month_num - day - hmin ^ \
        year - month - day - hmin

    year_month_weekday_hmin = \
        year - month_num - weekday - hmin ^ \
        year - month - weekday - hmin ^ \
        year - month_num - ordinal - weekday - hmin ^ \
        year - month - ordinal - weekday - hmin

    month_day_hmin = \
        month - day - hmin ^ \
        month_num - day - hmin

    month_weekday_hmin = \
        month - weekday - hmin ^ \
        month_num - weekday - hmin ^ \
        month - ordinal - weekday - hmin ^ \
        month_num - ordinal - weekday - hmin

    year_month_day = \
        year - month_num - day ^ \
        year - month - day

    year_month_weekday = \
        year - month_num - weekday ^ \
        year - month - weekday ^ \
        year - month_num - ordinal - weekday ^ \
        year - month - ordinal - weekday

    year_month = \
        year - month_num ^ \
        year - month

    month_day = \
        month_num - day ^ \
        month - day

    month_weekday = \
        month_num - weekday ^ \
        month - weekday ^ \
        month_num - ordinal - weekday ^ \
        month - ordinal - weekday

    ordinal_weekday = \
        ordinal - weekday

    day_hmin = \
        day - hmin

    weekday_hmin = \
        weekday - hmin ^ \
        ordinal - weekday - hmin

    for parser_element in (
            year_month_day_hmin, year_month_weekday_hmin, month_day_hmin, month_weekday_hmin,
            year_month_day, year_month_weekday, year_month, month_day, month_weekday,
            ordinal_weekday, day_hmin, weekday_hmin):
        parser_element.setParseAction(_merge_time_masks)

    # Some examples of valid time mask expressions:
    #
    #     2016 dec fri 10:16
    #     2016
    #     fri 10:30
    #     9999 dec
    #     17 20:29
    #     2016 7 29 20:29

    time_mask = \
        year_month_day_hmin ^ \
        year_month_weekday_hmin ^ \
        month_day_hmin ^ \
        month_weekday_hmin ^ \
        year_month_day ^ \
        year_month_weekday ^ \
        year_month ^ \
        month_day ^ \
        month_weekday ^ \
        ordinal_weekday ^ \
        day_hmin ^ \
        weekday_hmin ^ \
        year ^ \
        month ^ \
        weekday ^ \
        hmin

    # Time masks are then made into time ranges using '-'.
    # The parse result of a time range is a function taking
    # a single datetime parameter and returning true if the
    # parameter matches the time range.
    #
    # Internally the function uses the time mask tuples
    # generated above, using a 'partial function' approach

    time_range_all = Literal('-').setParseAction(lambda: lambda d: True)

    time_range_ge = time_mask - dash

    time_range_ge.setParseAction(
        lambda t: lambda d: _datetime_in_range(t[0], d, None))

    time_range_from_to = time_mask - dash - time_mask

    time_range_from_to.addCondition(
        lambda t: _time_masks_are_compatible(t[0], t[1]))

    time_range_from_to.addParseAction(
        lambda t: lambda d: _datetime_in_range(
            t[0], d, _merge_time_masks([t[0], t[1]])))

    time_range_le = dash - time_mask

    time_range_le.setParseAction(
        lambda t: lambda d: _datetime_in_range(None, d, t[0]))

    time_range_eq = time_mask.copy()
    time_range_eq.setParseAction(
        lambda t: lambda d: _datetime_in_range(t[0], d, t[0]))

    # Some examples of valid time range expressions:
    #
    #   -
    #   2016
    #   2016 -
    #   2016 - 2017
    #   - 2017

    time_range = time_range_all ^ \
                 time_range_eq ^ \
                 time_range_from_to ^ \
                 time_range_ge ^ \
                 time_range_le ^ \
                 time_mask

    # Use handy helper function provided to make infix expressions
    # easy to parse. The terms (double nested for some reason) are
    # all test functions created from time ranges. Note operators
    # are listed in descending precedence

    # Note: Re-reading http://pyparsing.wikispaces.com/share/view/73472016 I realised that the
    # issue in RB-726 was simply that when infixNotation() encounters a and b and c it passes
    # [a, b, c] to the and_op action, and all we have to do is adjust our action code to take variable
    # length lists of operands into account. Making this simple change restores the correct
    # interpretation of expressions such as 'jan or mar or dec'

    switch_exp = infixNotation(
        time_range,
        [
            (not_op, 1, opAssoc.RIGHT,
             not_op_action),
            (and_op, 2, opAssoc.LEFT,
             and_op_action),
            (or_op, 2, opAssoc.LEFT,
             or_op_action)
        ]
    )

    # Return the function we've built, which will be the first
    # item in the result list

    try:
        return switch_exp.parseString(expression, True)[0]
    except (ParseException, ParseSyntaxException) as exception:
        raise InvalidExpression(expression, exception)


# t[0] is an array of returned parse actions f(test_date) -> boolean
# representing the operands of not/and/or. They return a similar lambda function that
# applies the logical operator to the results of calling the operand functions with a
# test date. Note that "a and b and c and d" results in a single call to and_op_action
# with t[0] = [a, b, c, d]

def not_op_action(t):
    return lambda test_date: \
        not t[0][0](test_date)


def and_op_action(t):
    return lambda test_date: \
        reduce(lambda l_opr, r_opr:
                (l_opr if isinstance(l_opr, bool) else l_opr(test_date))
                and r_opr(test_date), t[0])


def or_op_action(t):
    return lambda test_date: \
        reduce(lambda l_opr, r_opr:
                (l_opr if isinstance(l_opr, bool) else l_opr(test_date))
                or r_opr(test_date), t[0])
