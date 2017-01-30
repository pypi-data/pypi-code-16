#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014-2017 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr

"""
########
Timeline
########

.. plot:: pyplots/timeline.py

:class:`pyannote.core.Timeline` instances are ordered sets of non-empty
segments:

  - ordered, because segments are sorted by start time (and end time in case of tie)
  - set, because one cannot add twice the same segment
  - non-empty, because one cannot add empty segments (*i.e.* start >= end)

There are two ways to define the timeline depicted above:

.. ipython::

  In [25]: from pyannote.core import Timeline, Segment

  In [26]: timeline = Timeline()
     ....: timeline.add(Segment(1, 5))
     ....: timeline.add(Segment(6, 8))
     ....: timeline.add(Segment(12, 18))
     ....: timeline.add(Segment(7, 20))
     ....:

  In [27]: segments = [Segment(1, 5), Segment(6, 8), Segment(12, 18), Segment(7, 20)]
     ....: timeline = Timeline(segments=segments, uri='my_audio_file')  # faster
     ....:

  In [9]: for segment in timeline:
     ...:     print(segment)
     ...:
  [ 00:00:01.000 -->  00:00:05.000]
  [ 00:00:06.000 -->  00:00:08.000]
  [ 00:00:07.000 -->  00:00:20.000]
  [ 00:00:12.000 -->  00:00:18.000]


.. note::

  The optional *uri*  keyword argument can be used to remember which document it describes.

Several convenient methods are available. Here are a few examples:

.. ipython::

  In [3]: timeline.extent()    # extent
  Out[3]: <Segment(1, 20)>

  In [5]: timeline.support()  # support
  Out[5]: <Timeline(uri=my_audio_file, segments=[<Segment(1, 5)>, <Segment(6, 20)>])>

  In [6]: timeline.duration()  # support duration
  Out[6]: 18


See :class:`pyannote.core.Timeline` for the complete reference.
"""

import warnings

from . import PYANNOTE_URI, PYANNOTE_SEGMENT
from banyan import SortedSet
from .interval_tree import TimelineUpdator
from .segment import Segment
from .json import PYANNOTE_JSON, PYANNOTE_JSON_CONTENT
from .util import string_generator, int_generator

# ignore Banyan warning
warnings.filterwarnings(
    'ignore', 'Key-type optimization',
    Warning, 'pyannote.core.timeline'
)
warnings.filterwarnings(
    'ignore', 'Key-type optimization',
    Warning, 'banyan'
)


# =====================================================================
# Timeline class
# =====================================================================


class Timeline(object):
    """
    Ordered set of segments.

    A timeline can be seen as an ordered set of non-empty segments (Segment).
    Segments can overlap -- though adding an already exisiting segment to a
    timeline does nothing.

    Parameters
    ----------
    segments : Segment iterator, optional
        initial set of segments
    uri : string, optional
        name of segmented resource

    Returns
    -------
    timeline : Timeline
        New timeline
    """

    @classmethod
    def from_df(cls, df, uri=None):
        segments = list(df[PYANNOTE_SEGMENT])
        timeline = cls(segments=segments, uri=uri)
        return timeline

    def __init__(self, segments=None, uri=None):

        super(Timeline, self).__init__()

        # sorted set of segments (as an augmented red-black tree)
        segments = [s for s in segments if s] if segments else []
        self._segments = SortedSet(items=segments,
                                   key_type=(float, float),
                                   updator=TimelineUpdator)

        # path to (or any identifier of) segmented resource
        self.uri = uri

    def __len__(self):
        """Number of segments

        >>> len(timeline)  # timeline contains three segments
        3
        """
        return self._segments.length()

    def __nonzero__(self):
        return self.__bool__()

    def __bool__(self):
        """Emptiness

        >>> if timeline:
        ...    # timeline is empty
        ... else:
        ...    # timeline is not empty
        """
        return self._segments.length() > 0

    def __iter__(self):
        """Iterate over segments (in chronological order)

        >>> for segment in timeline:
        ...     # do something with the segment

        See also
        --------
        :class:`pyannote.core.Segment` describes how segments are sorted.
        """
        return iter(self._segments)

    def __getitem__(self, k):
        """Get segment by index (in chronological order)

        >>> first_segment = timeline[0]
        >>> second_segment = timeline[1]

        Note
        ----
        Negative indexing is not supported.
        """
        return self._segments.kth(k)

    def __eq__(self, other):
        """Equality

        Two timelines are equal if and only if their segments are equal.

        >>> timeline1 = Timeline([Segment(0, 1), Segment(2, 3)])
        >>> timeline2 = Timeline([Segment(2, 3), Segment(0, 1)])
        >>> timeline3 = Timeline([Segment(2, 3)])
        >>> timeline1 == timeline2
        True
        >>> timeline1 == timeline3
        False
        """
        return self._segments == other._segments

    def __ne__(self, other):
        """Inequality"""
        return self._segments != other._segments

    def index(self, segment):
        """Get index of (existing) segment

        Parameters
        ----------
        segment : Segment
            Segment that is being looked for.

        Returns
        -------
        position : int
            Index of `segment` in timeline
        """
        return self._segments.index(segment)

    def add(self, segment):
        """Add a segment (in place)

        Parameters
        ----------
        segment : Segment
            Segment that is being added

        Returns
        -------
        self : Timeline
            Updated timeline.

        Note
        ----
        If the timeline already contains this segment, it will not be added
        again, as a timeline is meant to be a **set** of segments (not a list).

        If the segment is empty, it will not be added either, as a timeline
        only contains non-empty segments.
        """
        if segment:
            self._segments.add(segment)
        return self

    def update(self, timeline):
        """Add every segments of an existing timeline (in place)

        Parameters
        ----------
        timeline : Timeline
            Timeline whose segments are being added

        Returns
        -------
        self : Timeline
            Updated timeline

        Note
        ----
        Only segments that do not already exist will be added, as a timeline is
        meant to be a **set** of segments (not a list).

        """
        self._segments.update(timeline._segments)
        return self

    def union(self, timeline):
        """Create new timeline made of union of segments

        Parameters
        ----------
        timeline : Timeline
            Timeline whose segments are being added

        Returns
        -------
        union : Timeline
            New timeline containing the union of both timelines.

        Note
        ----
        This does the same as timeline.update(...) except it returns a new
        timeline, and the original one is not modified.
        """
        segments = self._segments.union(timeline._segments)
        return Timeline(segments=segments, uri=self.uri)

    def co_iter(self, other):
        """Iterate over pairs of intersecting segments

        >>> timeline1 = Timeline([Segment(0, 2), Segment(1, 2), Segment(3, 4)])
        >>> timeline2 = Timeline([Segment(1, 3), Segment(3, 5)])
        >>> for segment1, segment2 in timeline1.co_iter(timeline2):
        ...     print(segment1, segment2)
        (<Segment(0, 2)>, <Segment(1, 3)>)
        (<Segment(1, 2)>, <Segment(1, 3)>)
        (<Segment(3, 4)>, <Segment(3, 5)>)

        Parameters
        ----------
        other : Timeline
            Second timeline

        Returns
        -------
        iterable : (Segment, Segment) iterable
            Yields pairs of intersecting segments in chronological order.
        """
        for segment, other_segment in self._segments.co_iter(other._segments):
            yield segment, other_segment

    def crop_iter(self, support, mode='intersection', returns_mapping=False):
        """Like `crop` but returns a segment iterator instead

        See also
        --------
        :func:`pyannote.core.Timeline.crop`
        """

        if isinstance(support, Segment):
            support = Timeline(segments=[support], uri=self.uri)
            for yielded in self.crop_iter(support, mode=mode,
                                          returns_mapping=returns_mapping):
                yield yielded

        elif isinstance(support, Timeline):

            if mode == 'loose':
                for segment, _ in self.co_iter(support):
                    yield segment

            elif mode == 'strict':
                for segment, other_segment in self.co_iter(support):
                    if segment in other_segment:
                        yield segment

            elif mode == 'intersection':
                if returns_mapping:
                    for segment, other_segment in self.co_iter(support):
                        mapped_to = segment & other_segment
                        yield segment, mapped_to
                else:
                    for segment, other_segment in self.co_iter(support):
                        yield segment & other_segment

            else:
                raise NotImplementedError("unsupported mode: '%s'" % mode)

    def crop(self, support, mode='intersection', returns_mapping=False, mapping=False):
        """Crop timeline to new support

        Parameters
        ----------
        support : Segment or Timeline
            If `support` is a `Timeline`, its support is used.
        mode : {'strict', 'loose', 'intersection'}, optional
            Controls how segments that are not fully included in `support` are
            handled. 'strict' mode only keeps fully included segments. 'loose'
            mode keeps any intersecting segment. 'intersection' mode keeps any
            intersecting segment but replace them by their actual intersection.
        returns_mapping : bool, optional
            In 'intersection' mode, return a dictionary whose keys are segments
            of the cropped timeline, and values are list of the original
            segments that were cropped. Defaults to False.

        Returns
        -------
        cropped : Timeline
            Cropped timeline
        mapping : dict
            When 'returns_mapping' is True, dictionary whose keys are segments
            of 'cropped', and values are lists of corresponding original
            segments.

        Examples
        --------

        >>> timeline = Timeline([Segment(0, 2), Segment(1, 2), Segment(3, 4)])
        >>> timeline.crop(Segment(1, 3))
        <Timeline(uri=None, segments=[<Segment(1, 2)>])>

        >>> timeline.crop(Segment(1, 3), mode='loose')
        <Timeline(uri=None, segments=[<Segment(0, 2)>, <Segment(1, 2)>])>

        >>> timeline.crop(Segment(1, 3), mode='strict')
        <Timeline(uri=None, segments=[<Segment(1, 2)>])>

        >>> cropped, mapping = timeline.crop(Segment(1, 3), returns_mapping=True)
        >>> print(mapping)
        {<Segment(1, 2)>: [<Segment(0, 2)>, <Segment(1, 2)>]}

        """

        if mapping:
            returns_mapping = mapping
            warnings.warn(
                "'mapping' parameter has been renamed to 'returns_mapping'.",
                DeprecationWarning)

        if mode == 'intersection' and returns_mapping:
            segments, mapping = [], {}
            for segment, mapped_to in self.crop_iter(support,
                                                     mode='intersection',
                                                     returns_mapping=True):
                segments.append(mapped_to)
                mapping[mapped_to] = mapping.get(mapped_to, list()) + [segment]
            return Timeline(segments=segments, uri=self.uri), mapping

        segments = [s for s in self.crop_iter(support, mode=mode)]
        return Timeline(segments=segments, uri=self.uri)

    def overlapping(self, t):
        """Get list of segments overlapping `t`

        Parameters
        ----------
        t : float
            Timestamp, in seconds.

        Returns
        -------
        segments : list
            List of all segments of timeline containing time t

        """
        return self._segments.overlapping(t)

    def __str__(self):
        """Human-readable representation

        >>> timeline = Timeline(segments=[Segment(0, 10), Segment(1, 13.37)])
        >>> print(timeline)
        [[ 00:00:00.000 -->  00:00:10.000]
         [ 00:00:01.000 -->  00:00:13.370]]

        """

        n = len(self._segments)
        string = "["
        for i, segment in enumerate(self._segments):
            string += str(segment)
            string += "\n " if i+1 < n else ""
        string += "]"
        return string

    def __repr__(self):
        """Computer-readable representation

        >>> Timeline(segments=[Segment(0, 10), Segment(1, 13.37)])
        <Timeline(uri=None, segments=[<Segment(0, 10)>, <Segment(1, 13.37)>])>

        """

        return "<Timeline(uri=%s, segments=%s)>" % (self.uri,
                                                    list(self._segments))

    def __contains__(self, included):
        """Inclusion

        Check whether every segment of `included` does exist in timeline.

        Parameters
        ----------
        included : Segment or Timeline
            Segment or timeline being checked for inclusion

        Returns
        -------
        contains : bool
            True if every segment in `included` exists in timeline,
            False otherwise

        Examples
        --------
        >>> timeline1 = Timeline(segments=[Segment(0, 10), Segment(1, 13.37)])
        >>> timeline2 = Timeline(segments=[Segment(0, 10)])
        >>> timeline1 in timeline2
        False
        >>> timeline2 in timeline1
        >>> Segment(1, 13.37) in timeline1
        True

        """

        if isinstance(included, Segment):
            return included in self._segments

        elif isinstance(included, Timeline):
            return self._segments.issuperset(included._segments)

        else:
            raise TypeError(
                'Checking for inclusion only supports Segment and '
                'Timeline instances')

    def empty(self):
        """Return an empty copy

        Returns
        -------
        empty : Timeline
            Empty timeline using the same 'uri' attribute.

        """
        return Timeline(uri=self.uri)

    def copy(self, segment_func=None):
        """Get a copy of the timeline

        If `segment_func` is provided, it is applied to each segment first.

        Parameters
        ----------
        segment_func : callable, optional
            Callable that takes a segment as input, and returns a segment.
            Defaults to identity function (segment_func(segment) = segment)

        Returns
        -------
        timeline : Timeline
            Copy of the timeline

        """

        # if segment_func is not provided
        # just add every segment
        if segment_func is None:
            return Timeline(segments=self._segments, uri=self.uri)

        # if is provided
        # apply it to each segment before adding them
        return Timeline(segments=[segment_func(s) for s in self._segments],
                        uri=self.uri)

    def extent(self):
        """Extent

        The extent of a timeline is the segment of minimum duration that
        contains every segments of the timeline. It is unique, by definition.
        The extent of an empty timeline is an empty segment.

        A picture is worth a thousand words::

            timeline
            |------|    |------|     |----|
              |--|    |-----|     |----------|

            timeline.extent()
            |--------------------------------|

        Returns
        -------
        extent : Segment
            Timeline extent

        Examples
        --------
        >>> timeline = Timeline(segments=[Segment(0, 1), Segment(9, 10)])
        >>> timeline.extent()
        <Segment(0, 10)>

        """
        return self._segments.extent()

    def support_iter(self):
        """Like `support` but returns a segment iterator instead

        See also
        --------
        :func:`pyannote.core.Timeline.support`
        """

        # The support of an empty timeline is an empty timeline.
        if not self:
            return

        # Principle:
        #   * gather all segments with no gap between them
        #   * add one segment per resulting group (their union |)
        # Note:
        #   Since segments are kept sorted internally,
        #   there is no need to perform an exhaustive segment clustering.
        #   We just have to consider them in their natural order.

        # Initialize new support segment
        # as very first segment of the timeline
        new_segment = self._segments.kth(0)

        for segment in self:

            # If there is no gap between new support segment and next segment,
            if not (segment ^ new_segment):
                # Extend new support segment using next segment
                new_segment |= segment

            # If there actually is a gap,
            else:
                yield new_segment

                # Initialize new support segment as next segment
                # (right after the gap)
                new_segment = segment

        # Add new segment to the timeline support
        yield new_segment

    def support(self):
        """Timeline support

        The support of a timeline is the timeline with the minimum number of
        segments with exactly the same time span as the original timeline. It
        is (by definition) unique and does not contain any overlapping
        segments.

        A picture is worth a thousand words::

            timeline
            |------|    |------|     |----|
              |--|    |-----|     |----------|

            timeline.support()
            |------|  |--------|  |----------|

        Returns
        -------
        support : Timeline
            Timeline support
        """
        segments = [s for s in self.support_iter()]
        return Timeline(segments=segments, uri=self.uri)

    def coverage(self):
        warnings.warn(
            '"coverage" has been renamed to "support".',
            DeprecationWarning)
        return self.support()

    def duration(self):
        """Timeline duration

        The timeline duration is the sum of the durations of the segments
        in the timeline support.

        Returns
        -------
        duration : float
            Duration of timeline support, in seconds.
        """

        # The timeline duration is the sum of the durations
        # of the segments in the timeline support.
        return sum(s.duration for s in self.support_iter())

    def gaps_iter(self, support=None):
        """Like `gaps` but returns a segment iterator instead

        See also
        --------
        :func:`pyannote.core.Timeline.gaps`

        """

        if support is None:
            support = self.extent()

        if not isinstance(support, (Segment, Timeline)):
            raise TypeError("unsupported operand type(s) for -':"
                            "%s and Timeline." % type(support).__name__)

        # segment support
        if isinstance(support, Segment):

            # `end` is meant to store the end time of former segment
            # initialize it with beginning of provided segment `support`
            end = support.start

            # support on the intersection of timeline and provided segment
            for segment in self.crop(support, mode='intersection').support():

                # add gap between each pair of consecutive segments
                # if there is no gap, segment is empty, therefore not added
                yield Segment(start=end, end=segment.start)

                # keep track of the end of former segment
                end = segment.end

            # add final gap (if not empty)
            yield Segment(start=end, end=support.end)

        # timeline support
        elif isinstance(support, Timeline):

            # yield gaps for every segment in support of provided timeline
            for segment in support.support():
                for gap in self.gaps_iter(support=segment):
                    yield gap

    def gaps(self, support=None, focus=None):
        """Gaps

        A picture is worth a thousand words::

            timeline
            |------|    |------|     |----|
              |--|    |-----|     |----------|

            timeline.gaps()
                   |--|        |--|

        Parameters
        ----------
        support : None, Segment or Timeline
            Support in which gaps are looked for. Defaults to timeline extent

        Returns
        -------
        gaps : Timeline
            Timeline made of all gaps from original timeline, and delimited
            by provided support

        See also
        --------
        :func:`pyannote.core.Timeline.extent`

        """

        if focus is not None:
            support = focus
            warnings.warn(
                "'focus' parameter has been renamed to 'support'.",
                DeprecationWarning)

        segments = [s for s in self.gaps_iter(support=support)]
        return Timeline(segments=segments, uri=self.uri)

    def segmentation(self):
        """Segmentation

        Create the unique timeline with same support and same set of segment
        boundaries as original timeline, but with no overlapping segments.

        A picture is worth a thousand words::

            timeline
            |------|    |------|     |----|
              |--|    |-----|     |----------|

            timeline.segmentation()
            |-|--|-|  |-|---|--|  |--|----|--|

        Returns
        -------
        timeline : Timeline
            (unique) timeline with same support and same set of segment
            boundaries as original timeline, but with no overlapping segments.
        """
        # COMPLEXITY: O(n)
        support = self.support()

        # COMPLEXITY: O(n.log n)
        # get all boundaries (sorted)
        # |------|    |------|     |----|
        #   |--|    |-----|     |----------|
        # becomes
        # | |  | |  | |   |  |  |  |    |  |
        timestamps = set([])
        for (start, end) in self:
            timestamps.add(start)
            timestamps.add(end)
        timestamps = sorted(timestamps)

        # create new partition timeline
        # | |  | |  | |   |  |  |  |    |  |
        # becomes
        # |-|--|-|  |-|---|--|  |--|----|--|

        # start with an empty copy
        timeline = Timeline(uri=self.uri)

        if len(timestamps) == 0:
            return Timeline(uri=self.uri)

        segments = []
        start = timestamps[0]
        for end in timestamps[1:]:
            # only add segments that are covered by original timeline
            segment = Segment(start=start, end=end)
            if segment and support.overlapping(segment.middle):
                segments.append(segment)
            # next segment...
            start = end

        return Timeline(segments=segments, uri=self.uri)

    def to_annotation(self, generator='string', modality=None):
        """Turn timeline into an annotation

        Each segment is labeled by a unique label.

        Parameters
        ----------
        generator : 'string', 'int', or iterable, optional
            If 'string' (default) generate string labels. If 'int', generate
            integer labels. If iterable, use it to generate labels.
        modality : str, optional

        Returns
        -------
        annotation : Annotation
            Annotation
        """

        from .annotation import Annotation
        annotation = Annotation(uri=self.uri, modality=modality)
        if generator == 'string':
            generator = string_generator()
        elif generator == 'int':
            generator = int_generator()

        for segment in self:
            annotation[segment] = next(generator)

        return annotation

    def for_json(self):
        """Serialization

        See also
        --------
        :mod:`pyannote.core.json`
        """

        data = {PYANNOTE_JSON: self.__class__.__name__}
        data[PYANNOTE_JSON_CONTENT] = [s.for_json() for s in self]

        if self.uri:
            data[PYANNOTE_URI] = self.uri

        return data

    @classmethod
    def from_json(cls, data):
        """Deserialization

        See also
        --------
        :mod:`pyannote.core.json`
        """

        uri = data.get(PYANNOTE_URI, None)
        segments = [Segment.from_json(s) for s in data[PYANNOTE_JSON_CONTENT]]
        return cls(segments=segments, uri=uri)

    def _repr_png_(self):
        """IPython notebook support

        See also
        --------
        :mod:`pyannote.core.notebook`
        """

        from .notebook import repr_timeline
        return repr_timeline(self)
