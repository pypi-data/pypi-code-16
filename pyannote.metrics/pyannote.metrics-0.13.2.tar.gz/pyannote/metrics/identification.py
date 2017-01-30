#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2012-2017 CNRS

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

from __future__ import unicode_literals

from .base import BaseMetric
from .base import Precision, PRECISION_RETRIEVED, PRECISION_RELEVANT_RETRIEVED
from .base import Recall, RECALL_RELEVANT, RECALL_RELEVANT_RETRIEVED
from .matcher import LabelMatcher, \
    MATCH_TOTAL, MATCH_CORRECT, MATCH_CONFUSION, \
    MATCH_MISSED_DETECTION, MATCH_FALSE_ALARM
from .utils import UEMSupportMixin

IER_TOTAL = MATCH_TOTAL
IER_CORRECT = MATCH_CORRECT
IER_CONFUSION = MATCH_CONFUSION
IER_FALSE_ALARM = MATCH_FALSE_ALARM
IER_MISS = MATCH_MISSED_DETECTION
IER_NAME = 'identification error rate'


class IdentificationErrorRate(UEMSupportMixin, BaseMetric):
    """Identification error rate

    ``ier = (wc x confusion + wf x false_alarm + wm x miss) / total``

    where
        - `confusion` is the total confusion duration in seconds
        - `false_alarm` is the total hypothesis duration where there are
        - `miss` is
        - `total` is the total duration of all tracks
        - wc, wf and wm are optional weights (default to 1)

    Parameters
    ----------
    collar : float, optional
        Duration (in seconds) of collars removed from evaluation around
        boundaries of reference segments.
    confusion, miss, false_alarm: float, optional
        Optional weights for confusion, miss and false alarm respectively.
        Default to 1. (no weight)
    """

    @classmethod
    def metric_name(cls):
        return IER_NAME

    @classmethod
    def metric_components(cls):
        return [
            IER_TOTAL,
            IER_CORRECT,
            IER_FALSE_ALARM, IER_MISS,
            IER_CONFUSION]

    def __init__(self, confusion=1., miss=1., false_alarm=1.,
                 collar=0., **kargs):

        super(IdentificationErrorRate, self).__init__()

        self.matcher_ = LabelMatcher()
        self.confusion = confusion
        self.miss = miss
        self.false_alarm = false_alarm
        self.collar = collar

    def compute_components(self, reference, hypothesis, uem=None, **kwargs):

        detail = self.init_components()

        R, H, common_timeline = self.uemify(
            reference, hypothesis, uem=uem, collar=self.collar,
            returns_timeline=True)

        # loop on all segments
        for segment in common_timeline:

            # segment duration
            duration = segment.duration

            # list of IDs in reference segment
            r = R.get_labels(segment, unique=False)

            # list of IDs in hypothesis segment
            h = H.get_labels(segment, unique=False)

            counts, _ = self.matcher_(r, h)

            detail[IER_TOTAL] += duration * counts[IER_TOTAL]
            detail[IER_CORRECT] += duration * counts[IER_CORRECT]
            detail[IER_CONFUSION] += duration * counts[IER_CONFUSION]
            detail[IER_MISS] += duration * counts[IER_MISS]
            detail[IER_FALSE_ALARM] += duration * counts[IER_FALSE_ALARM]

        return detail

    def compute_metric(self, detail):

        numerator = 1. * (
            self.confusion * detail[IER_CONFUSION] +
            self.false_alarm * detail[IER_FALSE_ALARM] +
            self.miss * detail[IER_MISS]
        )
        denominator = 1. * detail[IER_TOTAL]
        if denominator == 0.:
            if numerator == 0:
                return 0.
            else:
                return 1.
        else:
            return numerator / denominator


class IdentificationPrecision(UEMSupportMixin, Precision):
    """Identification Precision

    Parameters
    ----------
    collar : float, optional
        Duration (in seconds) of collars removed from evaluation around
        boundaries of reference segments.
    """

    def __init__(self, unknown=False, collar=0., **kwargs):
        super(IdentificationPrecision, self).__init__()
        self.collar = collar
        self.matcher_ = LabelMatcher()

    def compute_components(self, reference, hypothesis, uem=None, **kwargs):

        detail = self.init_components()

        R, H, common_timeline = self.uemify(
            reference, hypothesis, uem=uem, collar=self.collar,
            returns_timeline=True)

        # loop on all segments
        for segment in common_timeline:

            # segment duration
            duration = segment.duration

            # list of IDs in reference segment
            r = R.get_labels(segment, unique=False)

            # list of IDs in hypothesis segment
            h = H.get_labels(segment, unique=False)

            counts, _ = self.matcher_(r, h)

            detail[PRECISION_RETRIEVED] += duration * len(h)
            detail[PRECISION_RELEVANT_RETRIEVED] += \
                duration * counts[IER_CORRECT]

        return detail


class IdentificationRecall(UEMSupportMixin, Recall):
    """Identification Recall

    Parameters
    ----------
    collar : float, optional
        Duration (in seconds) of collars removed from evaluation around
        boundaries of reference segments.
    """

    def __init__(self, collar=0., **kwargs):
        super(IdentificationRecall, self).__init__()
        self.collar = collar
        self.matcher_ = LabelMatcher()

    def compute_components(self, reference, hypothesis, uem=None, **kwargs):

        detail = self.init_components()

        R, H, common_timeline = self.uemify(
            reference, hypothesis, uem=uem, collar=self.collar,
            returns_timeline=True)

        # loop on all segments
        for segment in common_timeline:

            # segment duration
            duration = segment.duration

            # list of IDs in reference segment
            r = R.get_labels(segment, unique=False)

            # list of IDs in hypothesis segment
            h = H.get_labels(segment, unique=False)

            counts, _ = self.matcher_(r, h)

            detail[RECALL_RELEVANT] += duration * counts[IER_TOTAL]
            detail[RECALL_RELEVANT_RETRIEVED] += duration * counts[IER_CORRECT]

        return detail
