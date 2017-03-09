__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Oct 20, 2016 11:42$"


import itertools
import math

import toolz.itertoolz

from toolz.itertoolz import (
    accumulate,
    concat,
    count,
    first,
    peek,
    sliding_window,
)

from builtins import (
    range,
    map,
    zip,
)

from future.moves.itertools import (
    zip_longest,
)


def generator(it):
    """ Creates a generator type from the iterable.

    Args:

        it(iterable):            An iterable to make a generator.

    Returns:

        generator:               A generator made from the iterable.

    Examples:

        >>> generator(range(5))  # doctest: +ELLIPSIS
        <generator object generator at 0x...>

        >>> list(generator(range(5)))
        [0, 1, 2, 3, 4]
    """

    for each in it:
        yield each


def empty():
    """ Creates an empty iterator.

    Examples:

        >>> list(empty())
        []
    """

    return iter([])


def single(val):
    """ Creates an iterator with a single value.

    Args:

        val(any):               Single value to add to the iterator.

    Returns:

        iterable:               An iterable yielding the single value.

    Examples:

        >>> list(single(1))
        [1]
    """

    yield val


def cycles(seq, n=1):
    """ Cycles through the sequence n-times.

    Basically the same as ``itertools.cycle`` except that this sets
    an upper limit on how many cycles will be done.

    Note:

        If ``n`` is `None`, this is identical to ``itertools.cycle``.

    Args:

        seq(iterable):           The sequence to grab items from.
        n(integral):             Number of times to cycle through.

    Returns:

        generator:               The cycled sequence generator.

    Examples:

        >>> list(cycles([1, 2, 3], 2))
        [1, 2, 3, 1, 2, 3]
    """

    if n is None:
        return(itertools.cycle(seq))

    assert (n >= 0), "n must be positive, but got n = " + repr(n)
    assert ((n % 1) == 0), "n must be an integer, but got n = " + repr(n)

    return concat(itertools.tee(seq, n))


def duplicate(seq, n=1):
    """ Gets each element multiple times.

    Like ``itertools.repeat`` this will repeat each element n-times.
    However, it will do this for each element of the sequence.

    Args:

         seq(iterable):           The sequence to grab items from.
         n(integral):             Number of repeats for each element.

    Returns:

         generator:               A generator of repeated elements.

    Examples:

         >>> list(duplicate([1, 2, 3], 2))
         [1, 1, 2, 2, 3, 3]
    """

    assert (n >= 0), "n must be positive, but got n = " + repr(n)
    assert ((n % 1) == 0), "n must be an integer, but got n = " + repr(n)

    return concat(map(lambda _: itertools.repeat(_, n), seq))


def split(n, seq):
    """ Splits the sequence around element n.

    Provides 3 ``iterable``s in return.

    1. Everything before the ``n``-th value.
    2. An ``iterable`` with just the ``n``-th value.
    3. Everything after the ``n``-th value.

    Args:

         n(integral):                   Index to split the iterable at.
         seq(iterable):                 The sequence to split.

    Returns:

         ``tuple`` of ``iterable``s:    Each portion of the iterable
                                        around the index.

    Examples:

         >>> list(map(tuple, split(2, range(5))))
         [(0, 1), (2,), (3, 4)]

         >>> list(map(tuple, split(2, [10, 20, 30, 40, 50])))
         [(10, 20), (30,), (40, 50)]
    """

    front, middle, back = itertools.tee(seq, 3)

    front = itertools.islice(front, 0, n)
    middle = itertools.islice(middle, n, n + 1)
    back = itertools.islice(back, n + 1, None)

    return front, middle, back


def indices(*sizes):
    """ Iterates over a length/shape.

        Takes a size or sizes (unpacked shape) and iterates through all
        combinations of the indices.

        Args:
            *sizes(int):            list of sizes to iterate over.

        Returns:
            iterable:               an iterator over the sizes.


        Examples:

            >>> list(indices(3, 2))
            [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    """

    return(itertools.product(*[range(_) for _ in sizes]))


def pad(seq, before=0, after=0, fill=None):
    """ Pads a sequence by a fill value before and/or after.

    Pads the sequence before and after using the fill value provided
    by ``fill`` up to the lengths specified by ``before`` and
    ``after``. If either ``before`` or ``after`` is ``None``, pad
    the fill value infinitely on the respective end.

    Note:
        If ``before``is ``None``, the sequence will only be the fill
        value.

    Args:

        seq(iterable):          Sequence to pad.
        before(integral):       Amount to pad before.
        after(integral):        Amount to pad after.
        fill(any):              Some value to pad with.

    Returns:

        iterable:               A sequence that has been padded.

    Examples:

        >>> list(pad(range(2, 4), before=1, after=2, fill=0))
        [0, 2, 3, 0, 0]

    """

    all_seqs = []

    if before is None:
        return itertools.repeat(fill)
    elif before > 0:
        all_seqs.append(itertools.repeat(fill, before))

    all_seqs.append(seq)

    if after is None:
        all_seqs.append(itertools.repeat(fill))
    elif after > 0:
        all_seqs.append(itertools.repeat(fill, after))

    return concat(all_seqs)


def sliding_window_filled(seq,
                          n,
                          pad_before=False,
                          pad_after=False,
                          fillvalue=None):
    """ A sliding window with optional padding on either end..

        Args:
            seq(iter):                 an iterator or something that can
                                            be turned into an iterator

            n(int):                         number of generators to create as
                                            lagged

            pad_before(bool):               whether to continue zipping along
                                            the longest generator

            pad_after(bool):               whether to continue zipping along
                                            the longest generator

            fillvalue:                      value to use to fill generators
                                            shorter than the longest.

        Returns:
            generator object:               a generator object that will return
                                            values from each iterator.

        Examples:

            >>> list(sliding_window_filled(range(5), 2))
            [(0, 1), (1, 2), (2, 3), (3, 4)]

            >>> list(sliding_window_filled(range(5), 2, pad_after=True))
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, None)]

            >>> list(sliding_window_filled(range(5), 2, pad_before=True, pad_after=True))
            [(None, 0), (0, 1), (1, 2), (2, 3), (3, 4), (4, None)]
    """

    if pad_before and pad_after:
        seq = pad(
            seq,
            before=(n - 1),
            after=(n - 1),
            fill=fillvalue
        )
    elif pad_before:
        seq = pad(
            seq,
            before=(n - 1),
            fill=fillvalue
        )
    elif pad_after:
        seq = pad(
            seq,
            after=(n - 1),
            fill=fillvalue
        )

    return(sliding_window(n, seq))


def subrange(start, stop=None, step=None, substep=None):
    """
        Generates start and stop values for each subrange.

        Args:
            start(int):           First value in range (or last if only
                                  specified value)

            stop(int):            Last value in range

            step(int):            Step between each range

            substep(int):         Step within each range

        Yields:
            range:             A subrange within the larger range.

        Examples:
            >>> list(map(list, subrange(5)))
            [[0], [1], [2], [3], [4]]

            >>> list(map(list, subrange(0, 12, 3, 2)))
            [[0, 2], [3, 5], [6, 8], [9, 11]]
    """

    if stop is None:
        stop = start
        start = 0

    if step is None:
        step = 1

    if substep is None:
        substep = 1

    range_ends = itertools.chain(range(start, stop, step), [stop])

    for i, j in sliding_window(2, range_ends):
        yield(range(i, j, substep))


def disperse(seq):
    """
        Similar to range except that it recursively proceeds through the given
        range in such a way that values that follow each other are preferably
        not only non-sequential, but fairly different. This does not always
        work with small ranges, but works nicely with large ranges.

        Args:
            a(int):              the lower bound of the range
            b(int):              the upper bound of the range

        Returns:
            result(generator):   a generator that can be used to iterate
                                 through the sequence.

        Examples:

            >>> list(disperse(range(10)))
            [0, 5, 8, 3, 9, 4, 6, 1, 7, 2]
    """

    try:
        len_seq = len(seq)
    except TypeError:
        seq, len_seq = itertools.tee(seq)
        len_seq = count(len_seq)

    def disperse_helper(b, part_seq_1):
        if b != 0:
            half_diff = float(b) / 2.0

            mid_1 = int(math.floor(half_diff))
            mid_2 = int(math.ceil(half_diff))

            if 0 < mid_1 and b > mid_2:
                part_seq_1, part_seq_2 = itertools.tee(part_seq_1)

                front_mid_1_seq, mid_1_val, _ = split(mid_1, part_seq_1)
                _, mid_2_val, back_mid_2_seq = split(mid_2, part_seq_2)
                del _

                mid_2_val = itertools.tee(mid_2_val)
                back_mid_2_seq = concat([mid_2_val[0], back_mid_2_seq])
                mid_2_val = mid_2_val[1]

                yield(first(mid_2_val))

                for _1, _2 in zip(
                        disperse_helper(mid_1 - 0, front_mid_1_seq),
                        disperse_helper(b - mid_2, back_mid_2_seq)
                ):
                    yield(_2)
                    yield(_1)

                if mid_1 != mid_2:
                    yield(first(mid_1_val))

    if len_seq == 0:
        return

    val, seq = peek(seq)
    yield(val)

    for each in disperse_helper(len_seq, seq):
        yield(each)
