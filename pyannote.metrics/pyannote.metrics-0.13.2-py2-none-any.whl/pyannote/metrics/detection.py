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

from pyannote.core import Annotation, Timeline
from .base import BaseMetric
from .utils import UEMSupportMixin

DER_NAME = 'detection error rate'
DER_TOTAL = 'total'
DER_FALSE_ALARM = 'false alarm'
DER_MISS = 'miss'


class DetectionErrorRate(UEMSupportMixin, BaseMetric):
    """Detection error rate

    This metric can be used to evaluate binary classification tasks such as
    speech activity detection, for instance. Inputs are expected to only
    contain segments corresponding to the positive class (e.g. speech regions).
    Gaps in the inputs considered as the negative class (e.g. non-speech
    regions).

    It is computed as (fa + miss) / total, where fa is the duration of false
    alarm (e.g. non-speech classified as speech), miss is the duration of
    missed detection (e.g. speech classified as non-speech), and total is the
    total duration of the positive class in the reference.

    Parameters
    ----------
    collar : float, optional
        Duration (in seconds) of collars removed from evaluation around
        boundaries of reference segments (one half before, one half after).
    """

    @classmethod
    def metric_name(cls):
        return DER_NAME

    @classmethod
    def metric_components(cls):
        return [DER_TOTAL, DER_FALSE_ALARM, DER_MISS]

    def __init__(self, collar=0.0, **kwargs):
        super(DetectionErrorRate, self).__init__()
        self.collar = collar

    def compute_components(self, reference, hypothesis, uem=None, **kwargs):

        reference, hypothesis, uem = self.uemify(reference, hypothesis,
                                                 collar=self.collar, uem=uem,
                                                 returns_uem=True)

        reference = reference.get_timeline(copy=False).coverage()
        hypothesis = hypothesis.get_timeline(copy=False).coverage()

        reference_ = reference.gaps(focus=uem)
        hypothesis_ = hypothesis.gaps(focus=uem)

        false_positive = 0.
        for r_, h in reference_.co_iter(hypothesis):
            false_positive += (r_ & h).duration

        false_negative = 0.
        for r, h_ in reference.co_iter(hypothesis_):
            false_negative += (r & h_).duration

        detail = {}
        detail[DER_MISS] = false_negative
        detail[DER_FALSE_ALARM] = false_positive
        detail[DER_TOTAL] = reference.duration()

        return detail

    def compute_metric(self, detail):
        error = 1. * (detail[DER_FALSE_ALARM] + detail[DER_MISS])
        total = 1. * detail[DER_TOTAL]
        if total == 0.:
            if error == 0:
                return 0.
            else:
                return 1.
        else:
            return error / total


ACCURACY_NAME = 'detection accuracy'
ACCURACY_TRUE_POSITIVE = 'true positive'
ACCURACY_TRUE_NEGATIVE = 'true negative'
ACCURACY_FALSE_POSITIVE = 'false positive'
ACCURACY_FALSE_NEGATIVE = 'false negative'


class DetectionAccuracy(DetectionErrorRate):
    """Detection accuracy

    This metric can be used to evaluate binary classification tasks such as
    speech activity detection, for instance. Inputs are expected to only
    contain segments corresponding to the positive class (e.g. speech regions).
    Gaps in the inputs considered as the negative class (e.g. non-speech
    regions).

    It is computed as (tp + tn) / total, where tp is the duration of true
    positive (e.g. speech classified as speech), tn is the duration of true
    negative (e.g. non-speech classified as non-speech), and total is the total
    duration of the input signal.

    Parameters
    ----------
    collar : float, optional
        Duration (in seconds) of collars removed from evaluation around
        boundaries of reference segments (one half before, one half after).
    """

    @classmethod
    def metric_name(cls):
        return ACCURACY_NAME

    @classmethod
    def metric_components(cls):
        return [ACCURACY_TRUE_POSITIVE, ACCURACY_TRUE_NEGATIVE,
                ACCURACY_FALSE_POSITIVE, ACCURACY_FALSE_NEGATIVE]

    def compute_components(self, reference, hypothesis, uem=None, **kwargs):

        reference, hypothesis, uem = self.uemify(reference, hypothesis,
                                                 collar=self.collar, uem=uem,
                                                 returns_uem=True)

        reference = reference.get_timeline(copy=False).coverage()
        hypothesis = hypothesis.get_timeline(copy=False).coverage()

        reference_ = reference.gaps(focus=uem)
        hypothesis_ = hypothesis.gaps(focus=uem)

        true_positive = 0.
        for r, h in reference.co_iter(hypothesis):
            true_positive += (r & h).duration

        true_negative = 0.
        for r_, h_ in reference_.co_iter(hypothesis_):
            true_negative += (r_ & h_).duration

        false_positive = 0.
        for r_, h in reference_.co_iter(hypothesis):
            false_positive += (r_ & h).duration

        false_negative = 0.
        for r, h_ in reference.co_iter(hypothesis_):
            false_negative += (r & h_).duration

        detail = {}
        detail[ACCURACY_TRUE_NEGATIVE] = true_negative
        detail[ACCURACY_TRUE_POSITIVE] = true_positive
        detail[ACCURACY_FALSE_NEGATIVE] = false_negative
        detail[ACCURACY_FALSE_POSITIVE] = false_positive

        return detail

    def compute_metric(self, detail):
        numerator = 1. * (detail[ACCURACY_TRUE_NEGATIVE] +
                          detail[ACCURACY_TRUE_POSITIVE])
        denominator = 1. * (detail[ACCURACY_TRUE_NEGATIVE] +
                            detail[ACCURACY_TRUE_POSITIVE] +
                            detail[ACCURACY_FALSE_NEGATIVE] +
                            detail[ACCURACY_FALSE_POSITIVE])

        if denominator == 0.:
            return 1.
        else:
            return numerator / denominator


PRECISION_NAME = 'detection precision'
PRECISION_RETRIEVED = 'retrieved'
PRECISION_RELEVANT_RETRIEVED = 'relevant retrieved'


class DetectionPrecision(DetectionErrorRate):
    """Detection precision

    This metric can be used to evaluate binary classification tasks such as
    speech activity detection, for instance. Inputs are expected to only
    contain segments corresponding to the positive class (e.g. speech regions).
    Gaps in the inputs considered as the negative class (e.g. non-speech
    regions).

    It is computed as tp / (tp + fp), where tp is the duration of true positive
    (e.g. speech classified as speech), and fp is the duration of false
    positive (e.g. non-speech classified as speech).

    Parameters
    ----------
    collar : float, optional
        Duration (in seconds) of collars removed from evaluation around
        boundaries of reference segments (one half before, one half after).
    """

    @classmethod
    def metric_name(cls):
        return PRECISION_NAME

    @classmethod
    def metric_components(cls):
        return [PRECISION_RETRIEVED, PRECISION_RELEVANT_RETRIEVED]

    def compute_components(self, reference, hypothesis, uem=None, **kwargs):

        reference, hypothesis, uem = self.uemify(reference, hypothesis,
                                                 collar=self.collar, uem=uem,
                                                 returns_uem=True)

        reference = reference.get_timeline(copy=False).coverage()
        hypothesis = hypothesis.get_timeline(copy=False).coverage()

        reference_ = reference.gaps(focus=uem)

        true_positive = 0.
        for r, h in reference.co_iter(hypothesis):
            true_positive += (r & h).duration

        false_positive = 0.
        for r_, h in reference_.co_iter(hypothesis):
            false_positive += (r_ & h).duration

        detail = {}
        detail[PRECISION_RETRIEVED] = true_positive + false_positive
        detail[PRECISION_RELEVANT_RETRIEVED] = true_positive

        return detail

    def compute_metric(self, detail):
        relevant_retrieved = 1. * detail[PRECISION_RELEVANT_RETRIEVED]
        retrieved = 1. * detail[PRECISION_RETRIEVED]
        if retrieved == 0.:
            return 1.
        else:
            return relevant_retrieved / retrieved


RECALL_NAME = 'detection recall'
RECALL_RELEVANT = 'relevant'
RECALL_RELEVANT_RETRIEVED = 'relevant retrieved'


class DetectionRecall(DetectionErrorRate):
    """Detection recall

    This metric can be used to evaluate binary classification tasks such as
    speech activity detection, for instance. Inputs are expected to only
    contain segments corresponding to the positive class (e.g. speech regions).
    Gaps in the inputs considered as the negative class (e.g. non-speech
    regions).

    It is computed as tp / (tp + fn), where tp is the duration of true positive
    (e.g. speech classified as speech), and fn is the duration of false
    negative (e.g. speech classified as non-speech).

    Parameters
    ----------
    collar : float, optional
        Duration (in seconds) of collars removed from evaluation around
        boundaries of reference segments (one half before, one half after).
    """

    @classmethod
    def metric_name(cls):
        return RECALL_NAME

    @classmethod
    def metric_components(cls):
        return [RECALL_RELEVANT, RECALL_RELEVANT_RETRIEVED]

    def compute_components(self, reference, hypothesis, uem=None, **kwargs):

        reference, hypothesis, uem = self.uemify(reference, hypothesis,
                                                 collar=self.collar, uem=uem,
                                                 returns_uem=True)

        reference = reference.get_timeline(copy=False).coverage()
        hypothesis = hypothesis.get_timeline(copy=False).coverage()

        hypothesis_ = hypothesis.gaps(focus=uem)

        true_positive = 0.
        for r, h in reference.co_iter(hypothesis):
            true_positive += (r & h).duration

        false_negative = 0.
        for r, h_ in reference.co_iter(hypothesis_):
            false_negative += (r & h_).duration

        detail = {}
        detail[RECALL_RELEVANT] = true_positive + false_negative
        detail[RECALL_RELEVANT_RETRIEVED] = true_positive

        return detail

    def compute_metric(self, detail):
        relevant_retrieved = 1. * detail[RECALL_RELEVANT_RETRIEVED]
        relevant = 1. * detail[RECALL_RELEVANT]
        if relevant == 0.:
            if relevant_retrieved == 0:
                return 1.
            else:
                return 0.
        else:
            return relevant_retrieved / relevant
