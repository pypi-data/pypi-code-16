#encoding : utf-8
"""This module contains the core nelpy object definitions."""

__all__ = ['EventArray',
           'EpochArray',
           'AnalogSignal',
           'AnalogSignalArray',
           'SpikeTrainArray',
           'BinnedSpikeTrainArray']

# TODO: how should we organize our modules so that nelpy.objects.np does
# not shpw up, for example? If I type nelpy.object.<tab> I only want the
# actual objects to appear in the list. I think I do this with __all__,
# but still haven't quite figured it out yet. __all__ seems to mostly be
# useful for when we want to do from xxx import * in the package
# __init__ method

import warnings
import numpy as np

from abc import ABC, abstractmethod

from .utils import is_sorted, get_contiguous_segments, linear_merge

# Force warnings.warn() to omit the source code line in the message
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, \
    line=None: formatwarning_orig(
        message, category, filename, lineno, line='')

# from shapely.geometry import Point

########################################################################
# Helper functions
########################################################################

#----------------------------------------------------------------------#
#======================================================================#

# TODO: how should AnalogSignal handle its support? As an EpochArray?
# then what about binning issues? As explicit bin centers? As bin
# indices?
#
# it seems best to have a BinnedEpoch class, so that bin centers can be
# computed lazily when needed, and that duration etc. will be trivial,
# but we also really, REALLY need to be able to index AnalogSignal with
# a regular Epoch or EpochArray object, ...
#
# a nice finish to AnalogSignal would be to plot AnalogSignal on its
# support along with a smoothed version of it

### contested classes --- unclear whether these should exist or not:

# class Event
# class Epoch
# class Spike(Event)

def fsgetter(self):
    """(float) [generic getter] Sampling frequency."""
    if self._fs is None:
        warnings.warn("No sampling frequency has been specified!")
    return self._fs

def fssetter(self, val):
    """(float) [generic setter] Sampling frequency."""
    if self._fs == val:
        return
    try:
        if val <= 0:
            pass
    except:
        raise TypeError("sampling rate must be a scalar")
    if val <= 0:
        raise ValueError("sampling rate must be positive")

    # if it is the first time that a sampling rate is set, do not
    # modify anything except for self._fs:
    if self._fs is None:
        pass
    else:
        warnings.warn(
            "Sampling frequency has been updated! This will "
            "modify the spike times."
            )
        self._time = self.tdata / val
    self._fs = val

########################################################################
# class SpikeTrain
########################################################################
class SpikeTrain(ABC):
    """Base class for SpikeTrainArray and BinnedSpikeTrainArray.

    NOTE: This class can't really be instantiated, almost like a pseudo
    abstract class. In particular, during initialization it might fail
    because it checks the n_units of its derived classes to validate
    input to unit_ids and unit_labels. If NoneTypes are used, then you
    may actually succeed in creating an instance of this class, but it
    will be pretty useless.

    Parameters
    ----------
    fs: float, optional
        Sampling rate / frequency (Hz).
    unit_ids : list of int, optional
        Unit IDs preferabbly in integers
    unit_labels : list of str, optional
        Labels corresponding to units. Default casts unit_ids to str.
    label : str or None, optional
        Information pertaining to the source of the spike train.


    Attributes
    ----------
    n_units : int
        Number of units in spike train.
    unit_ids : list of int
        Unit integer IDs.
    unit_labels : list of str
        Labels corresponding to units. Default casts unit_ids to str.
    unit_tags : dict of tags and corresponding unit_ids
        Tags corresponding to units.
    issempty
    **********
    support
    **********
    fs: float
        Sampling frequency (Hz).
    label : str or None
        Information pertaining to the source of the spike train.
    """

    __attributes__ = ["_fs", "_unit_ids", "_unit_labels", "_unit_tags", "_label"]

    def __init__(self, *, fs=None, unit_ids=None, unit_labels=None,
                 unit_tags=None, label=None, empty=False):

        # if an empty object is requested, return it:
        if empty:
            for attr in self.__attributes__:
                exec("self." + attr + " = None")
            return

        # set initial fs to None
        self._fs = None
        # then attempt to update the fs; this does input validation:
        self.fs = fs

        # WARNING! we need to ensure that self.n_units can work BEFORE
        # we can set self.unit_ids or self.unit_labels, since those
        # setters check that the lengths of the inputs are consistent
        # with self.n_units.

        # inherit unit IDs if available, otherwise initialize to default
        if unit_ids is None:
            unit_ids = list(range(1,self.n_units + 1))

        unit_ids = np.array(unit_ids, ndmin=1)  # standardize unit_ids

        # if unit_labels is empty, default to unit_ids
        if unit_labels is None:
            unit_labels = unit_ids

        unit_labels = np.array(unit_labels, ndmin=1)  # standardize

        self.unit_ids = unit_ids
        self.unit_labels = unit_labels
        self._unit_tags = unit_tags  # no input validation yet
        self.label = label

    def __repr__(self):
        address_str = " at " + str(hex(id(self)))
        return "<base SpikeTrain" + address_str + ">"

    @abstractmethod
    def isempty(self):
        """(bool) Empty SpikeTrain."""
        return

    @abstractmethod
    def n_units(self):
        """(int) The number of units."""
        return

    @property
    def unit_ids(self):
        """Unit IDs contained in the SpikeTrain."""
        return self._unit_ids

    @unit_ids.setter
    def unit_ids(self, val):
        if len(val) != self.n_units:
            raise TypeError("unit_ids must be of length n_units")
        elif len(set(val)) < len(val):
            raise TypeError("duplicate unit_ids are not allowed")
        else:
            try:
                # cast to int:
                unit_ids = [int(id) for id in val]
            except TypeError:
                raise TypeError("unit_ids must be int-like")
        self._unit_ids = unit_ids

    @property
    def unit_labels(self):
        """Labels corresponding to units contained in the SpikeTrain."""
        if self._unit_labels is None:
            warnings.warn("unit labels have not yet been specified")
        return self._unit_labels

    @unit_labels.setter
    def unit_labels(self, val):
        if len(val) != self.n_units:
            raise TypeError("labels must be of length n_units")
        else:
            try:
                # cast to str:
                labels = [str(label) for label in val]
            except TypeError:
                raise TypeError("labels must be string-like")
        self._unit_labels = labels

    @property
    def unit_tags(self):
        """Tags corresponding to units contained in the SpikeTrain"""
        if self._unit_tags is None:
            warnings.warn("unit tags have not yet been specified")
        return self._unit_tags

    @property
    def support(self):
        """(nelpy.EpochArray) The support of the underlying spiketrain
        (in seconds).
         """
        return self._support

    @property
    def fs(self):
        """(float) Sampling rate / frequency (Hz)."""
        return fsgetter(self)

    @fs.setter
    def fs(self, val):
        """(float) Sampling rate / frequency (Hz)."""
        fssetter(self, val)

    @property
    def label(self):
        """Label pertaining to the source of the spike train."""
        if self._label is None:
            warnings.warn("label has not yet been specified")
        return self._label

    @label.setter
    def label(self, val):
        if val is not None:
            try:  # cast to str:
                label = str(val)
            except TypeError:
                raise TypeError("cannot convert label to string")
        else:
            label = val
        self._label = label

    def _unit_subset(self, unit_list):
        """Return a SpikeTrain restricted to a subset of units.

        Parameters
        ----------
        unit_list : array-like
            Array or list of unit_ids.
        """
        unit_subset_ids = []
        for unit in unit_list:
            try:
                id = self.unit_ids.index(unit)
            except ValueError:
                warnings.warn("unit_id " + str(unit) + " not found in SpikeTrain; ignoring")
                pass
            else:
                unit_subset_ids.append(id)

        new_unit_ids = np.asarray(self.unit_ids)[unit_subset_ids]
        new_unit_labels = np.asarray(self.unit_labels)[unit_subset_ids]

        if isinstance(self, SpikeTrainArray):
            if len(unit_subset_ids) == 0:
                warnings.warn("no units remaining in requested unit subset")
                return SpikeTrainArray(empty=True)

            spiketrainarray = SpikeTrainArray(empty=True)
            exclude = ["_tdata", "_time", "unit_ids", "unit_labels"]
            attrs = (x for x in self.__attributes__ if x not in exclude)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for attr in attrs:
                    exec("spiketrainarray." + attr + " = self." + attr)

            spiketrainarray._tdata = self.tdata[unit_subset_ids]
            spiketrainarray._time = self.time[unit_subset_ids]
            spiketrainarray._unit_ids = new_unit_ids
            spiketrainarray._unit_labels = new_unit_labels

            return spiketrainarray
        elif isinstance(self, BinnedSpikeTrainArray):
            if len(unit_subset_ids) == 0:
                warnings.warn("no units remaining in requested unit subset")
                return BinnedSpikeTrainArray(empty=True)

            binnedspiketrainarray = BinnedSpikeTrainArray(empty=True)
            exclude = ["_data", "unit_ids", "unit_labels"]
            attrs = (x for x in self.__attributes__ if x not in exclude)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for attr in attrs:
                    exec("binnedspiketrainarray." + attr + " = self." + attr)

            binnedspiketrainarray._data = self.data[unit_subset_ids,:]
            binnedspiketrainarray._unit_ids = new_unit_ids
            binnedspiketrainarray._unit_labels = new_unit_labels

            return binnedspiketrainarray
        else:
            raise NotImplementedError(
            "SpikeTrain._unit_slice() not supported for this type yet!")

########################################################################
# class EpochArray
########################################################################
class EpochArray:
    """An array of epochs, where each epoch has a start and stop time.

    Parameters
    ----------
    tdata : np.array
        If shape (n_epochs, 1) or (n_epochs,), the start time for each
        epoch (which then requires a duration to be specified).
        If shape (n_epochs, 2), the start and stop times for each epoch.
    fs : float, optional
        Sampling rate in Hz. If fs is passed as a parameter, then time
        is assumed to be in sample numbers instead of actual time.
    duration : np.array, float, or None, optional
        The length of the epoch. If (float) then the same duration is
        assumed for every epoch.
    meta : dict, optional
        Metadata associated with spiketrain.

    Attributes
    ----------
    time : np.array
        The start and stop times for each epoch. With shape (n_epochs, 2).
    tdata : np.array
        The start and stop tdata for each epoch. With shape (n_epochs, 2).
    fs: float
        Sampling frequency (Hz).
    meta : dict
        Metadata associated with spiketrain.
    """

    __attributes__ = ["_tdata", "_time", "_fs", "_meta"]

    def __init__(self, tdata=None, *, fs=None, duration=None,
                 meta=None, empty=False):

        # if an empty object is requested, return it:
        if empty:
            for attr in self.__attributes__:
                exec("self." + attr + " = None")
            return

        tdata = np.squeeze(tdata)  # coerce tdata into np.array

        # all possible inputs:
        # 1. single epoch, no duration    --- OK
        # 2. single epoch and duration    --- ERR
        # 3. multiple epochs, no duration --- OK
        # 4. multiple epochs and duration --- ERR
        # 5. single scalar and duration   --- OK
        # 6. scalar list and duratin list --- OK
        #
        # Q. won't np.squeeze make our life difficult?
        #
        # Strategy: determine if duration was passed. If so, try to see
        # if tdata can be coerced into right shape. If not, raise
        # error.
        # If duration was NOT passed, then do usual checks for epochs.

        if duration is not None:  # assume we received scalar starts
            tdata = np.array(tdata, ndmin=1)
            duration = np.squeeze(duration).astype(float)
            if duration.ndim == 0:
                duration = duration[..., np.newaxis]

            if tdata.ndim == 2 and duration.ndim == 1:
                raise ValueError(
                    "duration not allowed when using start and stop "
                    "times")

            if len(duration) > 1:
                if tdata.ndim == 1 and tdata.shape[0] != duration.shape[0]:
                    raise ValueError(
                        "must have same number of time and duration "
                        "tdata"
                        )
            if tdata.ndim == 1 and duration.ndim == 1:
                stop_epoch = tdata + duration
                tdata = np.hstack(
                    (tdata[..., np.newaxis], stop_epoch[..., np.newaxis]))
        else:  # duration was not specified, so assume we recived epochs

            # Note: if we have an empty array of tdata with no
            # dimension, then calling len(tdata) will return a
            # TypeError.
            try:
                # if no tdata were received, return an empty EpochArray:
                if len(tdata) == 0:
                    return EpochArray(empty=True)
            except TypeError:
                warnings.warn("unsupported type ("
                    + str(type(tdata))
                    + "); creating empty EpochArray")
                return EpochArray(empty=True)

            # Only one epoch is given eg EpochArray([3,5,6,10]) with no
            # duration and more than two values:
            if tdata.ndim == 1 and len(tdata) > 2:  # we already know duration is None
                raise TypeError(
                    "tdata of size (n_epochs, ) has to be accompanied by "
                    "a duration")

            if tdata.ndim == 1:  # and duration is None:
                tdata = np.array([tdata])

        if tdata.ndim > 2:
            raise ValueError("tdata must be a 1D or a 2D vector")

        # set initial fs to None
        self._fs = None
        # then attempt to update the fs; this does input validation:
        self.fs = fs

        try:
            if tdata[:, 0].shape[0] != tdata[:, 1].shape[0]:
                raise ValueError(
                    "must have the same number of start and stop times")
        except Exception:
            raise Exception("Unhandled EpochArray.__init__ case.")

        # TODO: what if start == stop? what will this break? This situation
        # can arise automatically when slicing a spike train with one or no
        # spikes, for example in which case the automatically inferred support
        # is a delta dirac

        if tdata.ndim == 2 and np.any(tdata[:, 1] - tdata[:, 0] < 0):
            raise ValueError("start must be less than or equal to stop")

        # if a sampling rate was given, relate time to tdata using fs:
        if fs is not None:
            time = tdata / fs
        else:
            time = tdata

        self._time = time
        self._tdata = tdata
        self._fs = fs
        self._meta = meta

    def __repr__(self):
        address_str = " at " + str(hex(id(self)))
        if self.isempty:
            return "<empty EpochArray" + address_str + ">"
        if self.n_epochs > 1:
            nstr = "%s epochs" % (self.n_epochs)
        else:
            nstr = "1 epoch"
        dstr = "totaling %s seconds" % self.duration
        return "<EpochArray%s: %s> %s" % (address_str, nstr, dstr)

    def __iter__(self):
        """EpochArray iterator initialization."""
        # initialize the internal index to zero when used as iterator
        self._index = 0
        return self

    def __next__(self):
        """EpochArray iterator advancer."""
        index = self._index
        if index > self.n_epochs - 1:
            raise StopIteration
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            epocharray = EpochArray(empty=True)

            exclude = ["_tdata", "_time"]
            attrs = (x for x in self.__attributes__ if x not in exclude)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for attr in attrs:
                    exec("epocharray." + attr + " = self." + attr)
            epocharray._tdata = np.array([self.tdata[index, :]])
            epocharray._time = np.array([self.time[index, :]])
        self._index += 1
        return epocharray

    def __getitem__(self, idx):
        """EpochArray index access.

        Accepts integers, slices, and EpochArrays.
        """
        if isinstance(idx, EpochArray):
            # case #: (self, idx):
            # case 0: idx.isempty == True
            # case 1: (fs, fs) = (None, const)
            # case 2: (fs, fs) = (const, None)
            # case 3: (fs, fs) = (None, None)
            # case 4: (fs, fs) = (const, const)
            # case 5: (fs, fs) = (constA, constB)
            if idx.isempty:  # case 0:
                return EpochArray(empty=True)
            if idx.fs != self.fs:  # cases (1, 2, 5):
                epocharray = EpochArray(empty=True)
                epocharray._tdata = idx._tdata
                epocharray._time = idx._time
                epoch = self.intersect(epocharray, boundaries=True)
            else:  # cases (3, 4)
                epoch = self.intersect(
                    epoch=idx,
                    boundaries=True
                    )
            if epoch.isempty:
                return EpochArray(empty=True)
            return epoch
        elif isinstance(idx, int):
            epocharray = EpochArray(empty=True)
            exclude = ["_tdata", "_time"]
            attrs = (x for x in self.__attributes__ if x not in exclude)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for attr in attrs:
                    exec("epocharray." + attr + " = self." + attr)
            try:
                epocharray._time = self.time[[idx], :]  # use np integer indexing! Cool!
                epocharray._tdata = self.tdata[[idx], :]
            except IndexError:
                # index is out of bounds, so return an empty EpochArray
                pass
            finally:
                return epocharray
        else:
            try:
                epocharray = EpochArray(empty=True)
                exclude = ["_tdata", "_time"]
                attrs = (x for x in self.__attributes__ if x not in exclude)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    for attr in attrs:
                        exec("epocharray." + attr + " = self." + attr)
                epocharray._time = np.array([self.starts[idx],
                                             self.stops[idx]]).T
                epocharray._tdata = np.array([self._tdatastarts[idx],
                                              self._tdatastops[idx]]).T
                return epocharray
            except Exception:
                raise TypeError(
                    'unsupported subsctipting type {}'.format(type(idx)))

    @property
    def meta(self):
        """Meta data associated with SpikeTrain."""
        if self._meta is None:
            warnings.warn("meta data is not available")
        return self._meta

    @meta.setter
    def meta(self, val):
        self._meta = val

    @property
    def fs(self):
        """(float) Sampling frequency."""
        return fsgetter(self)

    @fs.setter
    def fs(self, val):
        """(float) Sampling frequency."""
        fssetter(self, val)

    @property
    def tdata(self):
        """Epochs [start, stop] in sample numbers (default fs=1 Hz)."""
        return self._tdata

    @property
    def time(self):
        """Epoch times [start, stop] in seconds."""
        return self._time

    @property
    def centers(self):
        """(np.array) The center of each epoch."""
        if self.isempty:
            return []
        return np.mean(self.time, axis=1)

    @property
    def durations(self):
        """(np.array) The duration of each epoch."""
        if self.isempty:
            return 0
        return self.time[:, 1] - self.time[:, 0]

    @property
    def duration(self):
        """(float) The total duration of the epoch array."""
        if self.isempty:
            return 0
        return np.array(self.time[:, 1] - self.time[:, 0]).sum()

    @property
    def starts(self):
        """(np.array) The start of each epoch."""
        if self.isempty:
            return []
        return self.time[:, 0]

    @property
    def _tdatastarts(self):
        """(np.array) The start of each epoch, in tdata"""
        if self.isempty:
            return []
        return self.tdata[:, 0]

    @property
    def start(self):
        """(np.array) The start of the first epoch."""
        if self.isempty:
            return []
        return self.time[:, 0][0]

    @property
    def _tdatastart(self):
        """(np.array) The start of the first epoch, in tdata"""
        if self.isempty:
            return []
        return self.tdata[:, 0][0]

    @property
    def stops(self):
        """(np.array) The stop of each epoch."""
        if self.isempty:
            return []
        return self.time[:, 1]

    @property
    def _tdatastops(self):
        """(np.array) The stop of each epoch, in tdata"""
        if self.isempty:
            return []
        return self.tdata[:, 1]

    @property
    def stop(self):
        """(np.array) The stop of the last epoch."""
        if self.isempty:
            return []
        return self.time[:, 1][-1]

    @property
    def _tdatastop(self):
        """(np.array) The stop of the first epoch, in tdata"""
        return self.tdata[:, 0][0]

    @property
    def n_epochs(self):
        """(int) The number of epochs."""
        if self.isempty:
            return 0
        return len(self.time[:, 0])

    @property
    def issorted(self):
        """(bool) Left edges of epochs are sorted in ascending order."""
        return is_sorted(self.starts)

    @property
    def isempty(self):
        """(bool) Empty EpochArray."""
        try:
            return len(self.time) == 0
        except TypeError:
            return True  # this happens when self.time is None

    def copy(self):
        """(EpochArray) Returns a copy of the current epoch array."""
        newcopy = EpochArray(empty=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for attr in self.__attributes__:
                exec("newcopy." + attr + " = self." + attr)
        return newcopy

    def intersect(self, epoch, *, boundaries=True, meta=None):
        """Finds intersection (overlap) between two sets of epoch arrays.
        Sampling rates can be different.
        Parameters
        ----------
        epoch : nelpy.EpochArray
        boundaries : bool
            If True, limits start, stop to epoch start and stop.
        meta : dict, optional
            New dictionary of meta data for epoch ontersection.
        Returns
        -------
        intersect_epochs : nelpy.EpochArray
        """
        if self.isempty or epoch.isempty:
            warnings.warn('epoch intersection is empty')
            # TODO: copy everything except time? Wouldn't rest get
            # lost anyway due to no samples ==> return EpochArray(empty)?
            return EpochArray([], duration=[], meta=meta)

        new_starts = []
        new_stops = []
        epoch_a = self.copy().merge()
        epoch_b = epoch.copy().merge()

        for aa in epoch_a.time:
            for bb in epoch_b.time:
                if (aa[0] <= bb[0] < aa[1]) and (aa[0] < bb[1] <= aa[1]):
                    new_starts.append(bb[0])
                    new_stops.append(bb[1])
                elif (aa[0] < bb[0] < aa[1]) and (aa[0] < bb[1] > aa[1]):
                    new_starts.append(bb[0])
                    if boundaries:
                        new_stops.append(aa[1])
                    else:
                        new_stops.append(bb[1])
                elif (aa[0] > bb[0] < aa[1]) and (aa[0] < bb[1] < aa[1]):
                    if boundaries:
                        new_starts.append(aa[0])
                    else:
                        new_starts.append(bb[0])
                    new_stops.append(bb[1])
                elif (aa[0] >= bb[0] < aa[1]) and (aa[0] < bb[1] >= aa[1]):
                    if boundaries:
                        new_starts.append(aa[0])
                        new_stops.append(aa[1])
                    else:
                        new_starts.append(bb[0])
                        new_stops.append(bb[1])

        if not boundaries:
            new_starts = np.unique(new_starts)
            new_stops = np.unique(new_stops)

        epocharray = EpochArray(empty=True)
        exclude = ["_tdata", "_time", "_fs"]
        attrs = (x for x in self.__attributes__ if x not in exclude)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for attr in attrs:
                exec("epocharray." + attr + " = self." + attr)

        # case 1: (fs, fs) = (None, const)
        # case 2: (fs, fs) = (const, None)
        # case 3: (fs, fs) = (None, None)
        # case 4: (fs, fs) = (const, const)
        # case 5: (fs, fs) = (constA, constB)

        if self.fs != epoch.fs or self.fs is None:  # cases (1, 2, 3, 5)
            warnings.warn(
                "sampling rates are different; intersecting along "
                "time only and throwing away fs"
                )
            epocharray._time = np.hstack(
                [np.array(new_starts)[..., np.newaxis],
                 np.array(new_stops)[..., np.newaxis]])
            epocharray._tdata = epocharray._time
            epocharray._fs = None
        else:  # case (4, )
            epocharray._time = np.hstack(
                [np.array(new_starts)[..., np.newaxis],
                 np.array(new_stops)[..., np.newaxis]])
            epocharray._tdata = epocharray._time*self.fs
            epocharray._fs = self.fs

        return epocharray

    def merge(self, *, gap=0.0):
        """Merges epochs that are close or overlapping.
        Parameters
        ----------
        gap : float, optional
            Amount (in time) to consider epochs close enough to merge.
            Defaults to 0.0 (no gap).
        Returns
        -------
        merged_epochs : nelpy.EpochArray
        """
        if self.isempty:
            return self

        if gap < 0:
            raise ValueError("gap cannot be negative")

        epoch = self.copy()

        if self.fs is not None:
            gap = gap * self.fs

        stops = epoch._tdatastops[:-1] + gap
        starts = epoch._tdatastarts[1:]
        to_merge = (stops - starts) >= 0

        new_starts = [epoch._tdatastarts[0]]
        new_stops = []

        next_stop = epoch._tdatastops[0]
        for i in range(epoch.time.shape[0] - 1):
            this_stop = epoch._tdatastops[i]
            next_stop = max(next_stop, this_stop)
            if not to_merge[i]:
                new_stops.append(next_stop)
                new_starts.append(epoch._tdatastarts[i + 1])

        new_stops.append(epoch._tdatastops[-1])

        new_starts = np.array(new_starts)
        new_stops = np.array(new_stops)

        return EpochArray(
            new_starts,
            duration=new_stops - new_starts,
            fs=self.fs,
            meta=self.meta
            )

    def expand(self, amount, direction='both'):
        """Expands epoch by the given amount.
        Parameters
        ----------
        amount : float
            Amount (in time) to expand each epoch.
        direction : str
            Can be 'both', 'start', or 'stop'. This specifies
            which direction to resize epoch.
        Returns
        -------
        expanded_epochs : nelpy.EpochArray
        """
        if direction == 'both':
            resize_starts = self.time[:, 0] - amount
            resize_stops = self.time[:, 1] + amount
        elif direction == 'start':
            resize_starts = self.time[:, 0] - amount
            resize_stops = self.time[:, 1]
        elif direction == 'stop':
            resize_starts = self.time[:, 0]
            resize_stops = self.time[:, 1] + amount
        else:
            raise ValueError(
                "direction must be 'both', 'start', or 'stop'")

        return EpochArray(
            np.hstack((
                resize_starts[..., np.newaxis],
                resize_stops[..., np.newaxis]
                ))
            )

    def shrink(self, amount, direction='both'):
        """Shrinks epoch by the given amount.
        Parameters
        ----------
        amount : float
            Amount (in time) to shrink each epoch.
        direction : str
            Can be 'both', 'start', or 'stop'. This specifies
            which direction to resize epoch.
        Returns
        -------
        shrinked_epochs : nelpy.EpochArray
        """
        both_limit = min(self.durations / 2)
        if amount > both_limit and direction == 'both':
            raise ValueError("shrink amount too large")

        single_limit = min(self.durations)
        if amount > single_limit and direction != 'both':
            raise ValueError("shrink amount too large")

        return self.expand(-amount, direction)

    def join(self, epoch, meta=None):
        """Combines [and merges] two sets of epochs. Epochs can have
        different sampling rates.

        Parameters
        ----------
        epoch : nelpy.EpochArray
        meta : dict, optional
            New meta data dictionary describing the joined epochs.

        Returns
        -------
        joined_epochs : nelpy.EpochArray
        """

        if self.isempty:
            return epoch
        if epoch.isempty:
            return self

        if self.fs != epoch.fs:
            warnings.warn(
                "sampling rates are different; joining along time "
                "only and throwing away fs"
                )
            join_starts = np.concatenate(
                (self.time[:, 0], epoch.time[:, 0]))
            join_stops = np.concatenate(
                (self.time[:, 1], epoch.time[:, 1]))
            #TODO: calling merge() just once misses some instances.
            # I haven't looked carefully enough to know which edge cases
            # these are...
            # merge() should therefore be checked!
            # return EpochArray(join_starts, fs=None,
            # duration=join_stops - join_starts, meta=meta).merge()
            # .merge()
            return EpochArray(
                join_starts,
                fs=None,
                duration=join_stops - join_starts,
                meta=meta
                )
        else:
            join_starts = np.concatenate(
                (self.tdata[:, 0], epoch.tdata[:, 0]))
            join_stops = np.concatenate(
                (self.tdata[:, 1], epoch.tdata[:, 1]))

        # return EpochArray(join_starts, fs=self.fs, duration=
        # join_stops - join_starts, meta=meta).merge().merge()
        return EpochArray(
            join_starts,
            fs=self.fs,
            duration=join_stops - join_starts,
            meta=meta
            )

    def contains(self, value):
        """Checks whether value is in any epoch.

        Parameters
        ----------
        epochs: nelpy.EpochArray
        value: float or int

        Returns
        -------
        boolean

        """
        # TODO: consider vectorizing this loop, which should increase
        # speed, but also greatly increase memory? Alternatively, if we
        # could assume something about epochs being sorted, this can
        # also be made much faster than the current O(N)
        for start, stop in zip(self.starts, self.stops):
            if start <= value <= stop:
                return True
        return False
#----------------------------------------------------------------------#
#======================================================================#


########################################################################
# class EventArray
########################################################################
class EventArray:
    """Class description.

    Parameters
    ----------
    tdata : np.array
        If shape (n_epochs, 1) or (n_epochs,), the start time for each
        epoch.
        If shape (n_epochs, 2), the start and stop times for each epoch.
    fs : float, optional
        Sampling rate in Hz. If fs is passed as a parameter, then time
        is assumed to be in sample numbers instead of actual time.

    Attributes
    ----------
    time : np.array
        The start and stop times for each epoch. With shape (n_epochs, 2).
    """

    def __init__(self, *, tdata, fs=None, duration=None, meta=None):

        # if no tdata were received, return an empty EpochArray:
        if len(tdata) == 0:
            self._tdata = np.array([])
            self._time = np.array([])
            self._fs = None
            self._meta = None
            return

        self._fs = fs
        self._meta = meta

    def __repr__(self):
        address_str = " at " + str(hex(id(self)))
        if self.isempty:
            return "<empty EventArray" + address_str + ">"
        # return "<EventArray: %s> %s" % (nstr, dstr)
        return "<EventArray" + address_str + ">"

    def __getitem__(self, idx):
        raise NotImplementedError(
            'EventArray.__getitem__ not implemented yet')

    @property
    def isempty(self):
        """(bool) Empty EventArray."""
        raise NotImplementedError(
            'EventArray.isempty not implemented yet')
#----------------------------------------------------------------------#
#======================================================================#


########################################################################
# class AnalogSignal
########################################################################
class AnalogSignal:
    """A continuous, analog signal, with a regular sampling rate.

    Parameters
    ----------
    ydata : np.array(dtype=np.float)
    tdata : np.array(dtype=np.float), optional
        if fs is provided tdata is assumed to be sample numbers
        else it is assumed to be time but tdata can be a non time
        variable
    fs : float, optional
        Sampling rate in Hz. If fs is passed as a parameter, then time
        is assumed to be in sample numbers instead of actual time.
    support : EpochArray, optional
        EpochArray array on which spiketrain is defined.
        Default is [0, last spike] inclusive.
    step : int
        specifies step size of samples passed as tdata if fs is given,
        default set to 1. e.g. decimated data would have sample numbers
        every ten samples so step=10

    Attributes
    ----------
    ydata : np.array
        With shape (n_tdata,).
    tdata : np.array
        With shape (n_tdata,).
    time : np.array
        With shape (n_tdata,).
    fs : float, scalar, optional
        See Parameters
    support : EpochArray, optional
        See Parameters
    step : int
        See Parameters

    """
    __attributes__ = ['ydata','tdata','_time','fs','support','step']
    def __init__(self, ydata, *, tdata=None, fs=None, support=None, step=1):
        ydata = np.squeeze(ydata).astype(float)
        self._step=step


        # Note; if we have an empty array of ydata with no dimension,
        # then calling len(ydata) will return a TypeError
        try:
            # if no ydata are given return empty AnalogSignal
            if len(ydata) == 0:
                self._emptyAnalogSignal()
                return
        except TypeError:
            warnings.warn("unsupported type; creating empty AnalogSignal")
            self._emptyAnalogSignal()
            return

        # Note: if both tdata and ydata are given and dimensionality does not
        # match, then TypeError!
        if(tdata is not None):
            tdata = np.squeeze(tdata).astype(float)
            if(tdata.shape[0] != ydata.shape[0]):
                self._emptyAnalogSignal()
                raise TypeError("tdata and ydata size mismatch!")

        self.ydata = ydata

        # set initial fs to None
        self._fs = None
        # then attempt to update the fs; this does input validation:
        self.fs = fs

        # Note: time will be None if this is not a time series and fs isn't
        # specified set xtime to None.
        self._time = None
        time = None

        # Alright, let's handle all the possible parameter cases!
        if tdata is not None:
            if fs is not None:
                time = tdata / fs
                self.tdata = tdata
                if support is not None:
                    # tdata, fs, support passed properly
                    # self.support = support
                    self._time = time
                    self._restrict_to_epoch_array(epocharray=support)
                # tdata, fs and no support
                else:
                    warnings.warn("support created with given tdata and sampling rate, fs!")
                    self._time = time
                    self.support = EpochArray(get_contiguous_segments(tdata,
                        step=step), fs=fs)

            else:
                time = tdata
                self.tdata = tdata
                # tdata and support
                if support is not None:
                    # self.support = support
                    self._time = time
                    self._restrict_to_epoch_array(epocharray=support)
                    warnings.warn("support created with specified epoch array but no specified sampling rate")
                # tdata
                else:
                    warnings.warn("support created with just tdata! no sampling rate specified so support is entire range of signal")
                    self._time = time
                    self.support = EpochArray(np.array([0, time[-1]]))
        else:
            tdata = np.arange(0, len(ydata), 1)
            if fs is not None:
                time = tdata / fs
                # fs and support
                if support is not None:
                    self._emptyAnalogSignal()
                    raise TypeError("tdata must be passed if support is specified")
                # just fs
                else:
                    self._time = time
                    warnings.warn("support created with given sampling rate, fs")
                    self.support = EpochArray(np.array([0, time[-1]]))
            else:
                # just support
                if support is not None:
                    self._emptyAnalogSignal()
                    raise TypeError("tdata must be passed if support is "
                        +"specified")
                # just ydata
                else:
                    self._time = tdata
                    warnings.warn("support created with given ydata! support is entire signal")
                    self.support = EpochArray(np.array([0, tdata[-1]]))
            self.tdata = tdata

    def _restrict_to_epoch_array(self, *, epocharray=None, update=True):
        """Restrict self._time and self.ydata to an EpochArray. If no
        EpochArray is specified, self.support is used.

        Parameters
        ----------
        epocharray : EpochArray, optional
        	EpochArray on which to restrict AnalogSignal. Default is
        	self.support
        update : bool, optional
        	Overwrite self.support with epocharray if True (default).
        """
        if epocharray is None:
            epocharray = self.support
            update = False # support did not change; no need to update

        if epocharray.isempty:
            warnings.warn("Support specified is empty")
            self._emptyAnalogSignal()
            return

        indices = []
        for eptime in epocharray.time:
            t_start = eptime[0]
            t_stop = eptime[1]
            indices.append((self.time >= t_start) & (self.time <= t_stop))
        indices = np.any(np.column_stack(indices), axis=1)
        if np.count_nonzero(indices) < len(self._time):
            warnings.warn(
                'ignoring signal outside of support')
        self.ydata = self.ydata[indices]
        self._time = self._time[indices]
        self.tdata = self.tdata[indices]
        if update:
            self.support = epocharray

    def _emptyAnalogSignal(self):
        """Empty all the instance attributes for an empty object."""
        # if an empty object is requested, return it:
        for attr in self.__attributes__:
            exec("self." + attr + " = None")
        return

    def __repr__(self):
        address_str = " at " + str(hex(id(self)))
        if self.isempty:
            return "<empty AnalogSignal>"
        if self.n_epochs > 1:
            nstr = "%s epochs in analog signal" % (self.n_epochs)
        else:
            nstr = "1 epoch"
        dstr = "totalling %s seconds" % self.support.duration
        return "base <AnalogSignal %s: %s> %s" % (address_str, nstr,dstr)

    # @property
    # def ydata(self):
    #     return self.ydata

    # @ydata.setter
    # def ydata(self, val):
    #     """set ydata...user should NOT be able to call"""
    #     self.ydata = val

    # @property
    # def tdata(self):
    #     if self.tdata is None:
    #         warnings.warn("No tdata specified")
    #     return self.tdata

    @property
    def step(self):
        return self._step
    @property
    def time(self):
        if self._time is None:
            warnings.warn("No time calculated. This should be due to no tdata specified")
        return self._time

    # @property
    # def support(self):
    #     if self.support is None:
    #         warnings.warn("No support specified")
    #     return self.support

    @property
    def fs(self):
        """(float) Sampling frequency."""
        return fsgetter(self)

    @fs.setter
    def fs(self, val):
        """(float) Sampling rate / frequency (Hz)."""
        fssetter(self, val)

    @property
    def isempty(self):
        """(bool) checks length of ydata input"""
        return len(self.ydata) == 0

    @property
    def n_epochs(self):
        """(int) number of epochs in AnalogSignal"""
        return self.support.n_epochs


    def __iter__(self):
        """AnalogSignal iterator initialization"""
        # initialize the internal index to zero when used as iterator
        self._index = 0
        return self

    def __next__(self):
        """AnalogSignal iterator advancer."""
        index = self._index
        if index > self.n_epochs - 1:
            raise StopIteration
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            epoch = EpochArray(
                    np.array([self.support.tdata[index,:]])
                )
        self._index += 1
        return AnalogSignal(self.ydata,
                            fs=self.fs,
                            tdata=self.tdata,
                            support=epoch,
                            step=self._step
                )

    def __getitem__(self, idx):
        """AnalogSignal index access.
        Parameters
        Parameters
        ----------
        idx : EpochArray, int, slice
            intersect passed epocharray with support,
            index particular a singular epoch or multiple epochs with slice
        """
        epoch = self.support[idx]
        if epoch is None:
            warnings.warn("Index resulted in empty epoch array")
            return AnalogSignal(ydata = np.array([]),
                        tdata = np.array([]),
                        support = None,
                        fs = None
                    )
        else:
            return AnalogSignal(self.ydata,
                                fs=self.fs,
                                tdata=self.tdata,
                                support=epoch,
                                step=self._step
                    )

    def copy(self):
        return AnalogSignal(self.ydata,
                            fs = self.fs,
                            tdata=self.tdata,
                            support=self.support,
                            step=self._step
                )
    def mean(self):
        """Returns the mean of the entire signal."""
        return np.mean(self.ydata)

    def std(self):
        """Returns the standard deviation of the entire signal."""
        return np.std(self.ydata)

    def max(self):
        """Returns the maximum of the entire signal."""
        return np.max(self.ydata)

    def min(self):
        """Returns the minimum of the entire signal."""
        return np.min(self.ydata)

    def clip(self, min, max):
        """Clip (limit) the values in ydata to min and max as specified.

        Parameters
        ----------
        min : scalar
            Minimum value
        max : scalar
            Maximum value

        Returns
        ----------
        clipped_analogsignal : AnalogSignal
            AnalogSignal with the signal clipped with the elements of ydata, but where the values <
            min are replaced with min and the values > max are replaced
            with max.
        """
        new_ydata = np.clip(self.ydata, min, max)
        return AnalogSignal(new_ydata,
                                fs=self.fs,
                                tdata=self.tdata,
                                support=self.support,
                                step=self.step
                )

    def trim(self, start, stop=None, *, fs=None):
        """Trim the AnalogSignal to a single time/sample interval.

        Parameters
        ----------
        start : float or two element array-like
            (float) Left boundary of interval in time (seconds) if
            fs=None, otherwise left boundary is start / fs.
            (2 elements) Left and right boundaries in time (seconds) if
            fs=None, otherwise boundaries are left / fs. Stop must be
            None if 2 element start is used.
        stop : float, optional
            Right boundary of interval in time (seconds) if fs=None,
            otherwise right boundary is stop / fs.
        fs : float, optional
            Sampling rate in Hz.

        Returns
        -------
        trim : AnalogSignal
            The AnalogSignal on the interval [start, stop].

        Examples
        --------
        >>> as.trim([0, 3], fs=1)  # recommended for readability
        >>> as.trim(start=0, stop=3, fs=1)
        >>> as.trim(start=[0, 3])
        >>> as.trim(0, 3)
        >>> as.trim((0, 3))
        >>> as.trim([0, 3])
        >>> as.trim(np.array([0, 3]))
        """

        # TODO: do comprehensive input validation
        if stop is not None:
            try:
                start = np.array(start, ndmin=1)
                if len(start) != 1:
                    raise TypeError("start must be a scalar float")
            except TypeError:
                raise TypeError("start must be a scalar float")
            try:
                stop = np.array(stop, ndmin=1)
                if len(stop) != 1:
                    raise TypeError("stop must be a scalar float")
            except TypeError:
                raise TypeError("stop must be a scalar float")
        else:  # start must have two elements
            try:
                if len(np.array(start, ndmin=1)) > 2:
                    raise TypeError(
                        "unsupported input to AnalogSignalArray.trim()")
                stop = np.array(start[1], ndmin=1)
                start = np.array(start[0], ndmin=1)
                if len(start) != 1 or len(stop) != 1:
                    raise TypeError(
                        "start and stop must be scalar floats")
            except TypeError:
                raise TypeError(
                    "start and stop must be scalar floats")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            epoch = self.support.intersect(
                EpochArray(
                    [start, stop],
                    fs=fs))
            if not epoch.isempty:
                analogsignal = self[epoch]
            else:
                analogsignal = AnalogSignal([])
        return analogsignal

#----------------------------------------------------------------------#
#======================================================================#


########################################################################
# class AnalogSignalArray
########################################################################
class AnalogSignalArray:
    """Class description.

    Parameters
    ----------
    tdata : np.array
        If shape (n_epochs, 1) or (n_epochs,), the start time for each
        epoch.
        If shape (n_epochs, 2), the start and stop times for each epoch.
    fs : float, optional
        Sampling rate in Hz. If fs is passed as a parameter, then time
        is assumed to be in sample numbers instead of actual time.

    Attributes
    ----------
    time : np.array
        The start and stop times for each epoch. With shape (n_epochs, 2).
    """

    def __init__(self, *, tdata, fs=None, duration=None, meta=None):

        # if no tdata were received, return an empty EpochArray:
        if len(tdata) == 0:
            self._tdata = np.array([])
            self._time = np.array([])
            self._fs = None
            self._meta = None
            return

        self._fs = fs
        self._meta = meta

    def __repr__(self):
        if self.isempty:
            return "<empty AnalogSignalArray"
        # return "<AnalogSignalArray: %s> %s" % (nstr, dstr)
        return "<AnalogSignalArray"

    def __getitem__(self, idx):
        raise NotImplementedError(
            'AnalogSignalArray.__getitem__ not implemented yet')

    @property
    def isempty(self):
        """(bool) Empty AnalogSignalArray."""
        raise NotImplementedError(
            'AnalogSignalArray.isempty not implemented yet')
#----------------------------------------------------------------------#
#======================================================================#

########################################################################
# class SpikeTrainArray
########################################################################
class SpikeTrainArray(SpikeTrain):
    """A multiunit spiketrain array with shared support.

    Parameters
    ----------
    tdata : array (of length n_units) of np.array(dtype=np.float64)
        containing spike times in in seconds (unless fs=None).
    fs : float, optional
        Sampling rate in Hz. If fs is passed as a parameter, then time
        is assumed to be in sample numbers instead of actual time.
    support : EpochArray, optional
        EpochArray on which spiketrains are defined.
        Default is [0, last spike] inclusive.
    label : str or None, optional
        Information pertaining to the source of the spiketrain array.
    cell_type : list (of length n_units) of str or other, optional
        Identified cell type indicator, e.g., 'pyr', 'int'.
    unit_ids : list (of length n_units) of indices corresponding to
        curated data. If no unit_ids are specified, then [1,...,n_units]
        will be used. WARNING! The first unit will have index 1, not 0!
    meta : dict
        Metadata associated with spiketrain array.

    Attributes
    ----------
    time : array of np.array(dtype=np.float64) spike times in seconds.
        Array of length n_units, each entry with shape (n_tdata,)
    tdata : list of np.array(dtype=np.float64) spike times in tdata.
        Array of length n_units, each entry with shape (n_tdata,)
    support : EpochArray on which spiketrain array is defined.
    n_spikes: np.array(dtype=np.int) of shape (n_units,)
        Number of spikes in each unit.
    fs: float
        Sampling frequency (Hz).
    cell_types : np.array of str or other
        Identified cell type for each unit.
    label : str or None
        Information pertaining to the source of the spiketrain.
    meta : dict
        Metadata associated with spiketrain.
    """

    __attributes__ = ["_tdata", "_time", "_support"]
    __attributes__.extend(SpikeTrain.__attributes__)
    def __init__(self, tdata=None, *, fs=None, support=None,
                 unit_ids=None, unit_labels=None, unit_tags=None,
                 label=None, empty=False):

        # if an empty object is requested, return it:
        if empty:
            super().__init__(empty=True)
            for attr in self.__attributes__:
                exec("self." + attr + " = None")
            return

        def standardize_to_2d(data):
            data = np.squeeze(data)  # deals with extraneous dimensions
            data = np.array(data, ndmin=1)  # deals with extraneous
                # dimensions
            f1 = data.dtype is not np.dtype('O')  # True if single unit,
                # or if square array; False if jagged array
            # so how do we differentiate between square array and single
            # unit? Square array should have different #rows from
            # #elements
            f2 = data.shape[0] == data.size  # False if square array,
                # True otherwise
            if f1 and f2:  # single unit!
                data = np.array([data], ndmin=2)  # wrap single units
            elif not f1:  # jagged array
                # standardize input so that a list of lists is converted
                # to an array of arrays:
                data = np.array(
                    [np.array(st, ndmin=1, copy=False) for st in data])
            return data

        tdata = standardize_to_2d(tdata)

        # if only empty tdata were received AND no support, return empty
        # SpikeTrainArray:
        if np.sum([st.size for st in tdata]) == 0 and support is None:
            warnings.warn("no data; returning empty SpikeTrainArray")
            self = SpikeTrainArray(empty=True)
            return

        kwargs = {"fs": fs,
                  "unit_ids": unit_ids,
                  "unit_labels": unit_labels,
                  "unit_tags": unit_tags,
                  "label": label}

        # initialize super so that self.fs is set:
        self._time = tdata  # this is necessary so that super() can
            # determine self.n_units when initializing. self.time will
            # be updated later in __init__ to reflect subsequent changes
        super().__init__(**kwargs)

        # if a sampling rate was given, relate time to tdata using fs:
        if fs is not None:
            time = tdata / fs
        else:
            time = tdata

        # determine spiketrain array support:
        if support is None:
            # first_st = np.array([unit[0] for unit in tdata]).min()
            # BUG: if spiketrain is empty np.array([]) then unit[-1]
            # raises an error in the following:
            # FIX: list[-1] raises an IndexError for an empty list,
            # whereas list[-1:] returns an empty list.
            last_st = np.array([unit[-1:] for unit in tdata]).max()
            self._support = EpochArray(np.array([0, last_st]), fs=fs)
            # in the above, there's no reason to restrict to support
        else:
            # restrict spikes to only those within the spiketrain
            # array's support:
            self._support = support

            time, tdata = self._restrict_to_epoch_array(
                epocharray=support,
                time=time,
                tdata=tdata)

        # if no tdata remain after restricting to the support, return
        # an empty SpikeTrainArray:
        if np.sum([st.size for st in tdata]) == 0:
            return SpikeTrainArray(empty=True)

        # set self._tdata and self._time:
        self._time = time
        self._tdata = tdata

    def copy(self):
        """Returns a copy of the SpikeTrainArray."""
        newcopy = SpikeTrainArray(empty=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for attr in self.__attributes__:
                exec("newcopy." + attr + " = self." + attr)
        return newcopy

    def __iter__(self):
        """SpikeTrainArray iterator initialization."""
        # initialize the internal index to zero when used as iterator
        self._index = 0
        return self

    def __next__(self):
        """SpikeTrainArray iterator advancer."""
        index = self._index
        if index > self.support.n_epochs - 1:
            raise StopIteration
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            support = self.support[index]
            time, tdata = self._restrict_to_epoch_array(
                epocharray=support,
                time=self.time,
                tdata=self.tdata,
                copy=True
                )
            spiketrain = SpikeTrainArray(empty=True)
            exclude = ["_tdata", "_time", "_support"]
            attrs = (x for x in self.__attributes__ if x not in exclude)
            for attr in attrs:
                exec("spiketrain." + attr + " = self." + attr)
            spiketrain._tdata = tdata
            spiketrain._time = time
            spiketrain._support = support
        self._index += 1
        return spiketrain

    def __getitem__(self, idx):
        """SpikeTrainArray index access."""
        # TODO: allow indexing of form sta[4,1:5] so that the STs of
        # epochs 1 to 5 (exlcusive) are returned, for neuron id 4.

        if isinstance(idx, EpochArray):
            if idx.isempty:
                return SpikeTrainArray(empty=True)
            if idx.fs != self.support.fs:
                support = self.support.intersect(
                    epoch=EpochArray(idx.time, fs=None),
                    boundaries=True
                    )
            else:
                support = self.support.intersect(
                    epoch=idx,
                    boundaries=True
                    ) # what if fs of slicing epoch is different?
            if support.isempty:
                return SpikeTrainArray(empty=True)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                time, tdata = self._restrict_to_epoch_array(
                    epocharray=support,
                    time=self.time,
                    tdata=self.tdata,
                    copy=True
                    )
                spiketrain = SpikeTrainArray(empty=True)
                exclude = ["_tdata", "_time", "_support"]
                attrs = (x for x in self.__attributes__ if x not in exclude)
                for attr in attrs:
                    exec("spiketrain." + attr + " = self." + attr)
                spiketrain._tdata = tdata
                spiketrain._time = time
                spiketrain._support = support
            return spiketrain
        elif isinstance(idx, int):
            spiketrain = SpikeTrainArray(empty=True)
            exclude = ["_tdata", "_time", "_support"]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                attrs = (x for x in self.__attributes__ if x not in exclude)
                for attr in attrs:
                    exec("spiketrain." + attr + " = self." + attr)
                support = self.support[idx]
                spiketrain._support = support
            if (idx >= self.support.n_epochs) or idx < (-self.support.n_epochs):
                return spiketrain
            else:
                time, tdata = self._restrict_to_epoch_array(
                        epocharray=support,
                        time=self.time,
                        tdata=self.tdata,
                        copy=True
                        )
                spiketrain._tdata = tdata
                spiketrain._time = time
                spiketrain._support = support
                return spiketrain
        else:  # most likely slice indexing
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    support = self.support[idx]
                    time, tdata = self._restrict_to_epoch_array(
                        epocharray=support,
                        time=self.time,
                        tdata=self.tdata,
                        copy=True
                        )
                    spiketrain = SpikeTrainArray(empty=True)
                    exclude = ["_tdata", "_time", "_support"]
                    attrs = (x for x in self.__attributes__ if x not in exclude)
                    for attr in attrs:
                        exec("spiketrain." + attr + " = self." + attr)
                    spiketrain._tdata = tdata
                    spiketrain._time = time
                    spiketrain._support = support
                return spiketrain
            except Exception:
                raise TypeError(
                    'unsupported subsctipting type {}'.format(type(idx)))

    @property
    def isempty(self):
        """(bool) Empty SpikeTrainArray."""
        try:
            return np.sum([len(st) for st in self.time]) == 0
        except TypeError:
            return True  # this happens when self.time == None

    @property
    def n_units(self):
        """(int) The number of units."""
        return len(self.time)

    def flatten(self, *, unit_id=None, unit_label=None):
        """Collapse spike trains across units.

        WARNING! unit_tags are thrown away when flattening.

        Parameters
        ----------
        unit_id: (int)
            (unit) ID to assign to flattened spike train, default is 0.
        unit_label (str)
            (unit) Label for spike train, default is 'flattened'.
        """
        if self.n_units == 1:  # already flattened
            return self

        # default args:
        if unit_id is None:
            unit_id = 0
        if unit_label is None:
            unit_label = "flattened"

        spiketrainarray = SpikeTrainArray(empty=True)

        exclude = ["_tdata", "_time", "unit_ids", "unit_labels", "unit_tags"]
        attrs = (x for x in self.__attributes__ if x not in exclude)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for attr in attrs:
                exec("spiketrainarray." + attr + " = self." + attr)
        spiketrainarray._unit_ids = [unit_id]
        spiketrainarray._unit_labels = [unit_label]
        spiketrainarray._unit_tags = None

        # TODO: here we linear merge twice; once for tdata and once for
        # time. This is unneccessary, and can be optimized. But flatten()
        # shouldn't be called often, so it's low priority,
        allspikes = self.tdata[0]
        for unit in range(1,self.n_units):
            allspikes = linear_merge(allspikes, self.tdata[unit])
        alltimes = self.time[0]
        for unit in range(1,self.n_units):
            alltimes = linear_merge(alltimes, self.time[unit])

        spiketrainarray._tdata = np.array(list(allspikes), ndmin=2)
        spiketrainarray._time = np.array(list(alltimes), ndmin=2)
        return spiketrainarray

    def _restrict_to_epoch_array(self, *, epocharray, time, tdata,
                                 copy=True):
        """Returns time and tdata restricted to an EpochArray.

        Parameters
        ----------
        epocharray : EpochArray, optional
            EpochArray on which to restrict SpikeTrainArray. Default is
            self.support
        """
        # Potential BUG: not sure if time and tdata point to same
        # object (like when only time was passed to __init__), then
        # doing tdata[unit] = ... followed by time[unit] = ... might
        # be applying the shrinking twice, no? We need a thorough test
        # for this! And I need to understand the shared memory 100%.
        if copy:
            time = time.copy()
            tdata = tdata.copy()
        # BUG: this assumes multiple units for the enumeration to work
        for unit, st_time in enumerate(time):
            indices = []
            for eptime in epocharray.time:
                t_start = eptime[0]
                t_stop = eptime[1]
                indices.append((st_time >= t_start) & (st_time <= t_stop))
            indices = np.any(np.column_stack(indices), axis=1)
            if np.count_nonzero(indices) < len(st_time):
                warnings.warn(
                    'ignoring spikes outside of spiketrain support')
            tdata[unit] = tdata[unit][indices]
            time[unit] = time[unit][indices]
        return time, tdata

    def __repr__(self):
        address_str = " at " + str(hex(id(self)))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if self.isempty:
                return "<empty SpikeTrainArray" + address_str + ">"
            if self.fs is not None:
                fsstr = " at %s Hz" % self.fs
            else:
                fsstr = ""
            if self.label is not None:
                labelstr = " from %s" % self.label
            else:
                labelstr = ""
            numstr = " %s units" % self.n_units
        return "<SpikeTrainArray%s:%s>%s%s" % (address_str, numstr, fsstr, labelstr)

    def bin(self, *, ds=None):
        """Bin spiketrain array."""
        return BinnedSpikeTrainArray(self, ds=ds, empty=self.isempty)

    @property
    def tdata(self):
        """Spike times in sample numbers (default fs = 1 Hz)."""
        return self._tdata

    @property
    def time(self):
        """Spike times in seconds."""
        return self._time

    @property
    def n_spikes(self):
        """(np.array) The number of spikes in each unit."""
        if self.isempty:
            return 0
        return np.array([len(unit) for unit in self.time])

    @property
    def n_active(self):
        """Number of active units per epoch with shape (n_epochs,)."""
        raise NotImplementedError(
            'SpikeTrainArray.n_active not implemented yet')

    @property
    def issorted(self):
        """(bool) Sorted SpikeTrainArray."""
        return np.array(
            [is_sorted(spiketrain) for spiketrain in self.tdata]
            ).all()
#----------------------------------------------------------------------#
#======================================================================#


########################################################################
# class BinnedSpikeTrainArray
########################################################################
class BinnedSpikeTrainArray(SpikeTrain):
    """Binned spiketrain array.

    Parameters
    ----------
    fs : float, optional
        Sampling rate in Hz. If fs is passed as a parameter, then time
        is assumed to be in sample numbers instead of actual time.

    Attributes
    ----------
    time : np.array
        The start and stop times for each epoch. With shape (n_epochs, 2).
    """

    __attributes__ = ["_ds", "_bins", "_data", "_centers", "_support",
                      "_binnedSupport", "_spiketrainarray"]
    __attributes__.extend(SpikeTrain.__attributes__)

    def __init__(self, spiketrainarray=None, *, ds=None, empty=False):

        # if an empty object is requested, return it:
        if empty:
            super().__init__(empty=True)
            for attr in self.__attributes__:
                exec("self." + attr + " = None")
            return

        if not isinstance(spiketrainarray, SpikeTrainArray):
            raise TypeError(
                'spiketrainarray must be a nelpy.SpikeTrainArray object.')

        self._ds = None
        self._centers = np.array([])

        with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                kwargs = {"fs": spiketrainarray.fs,
                        "unit_ids": spiketrainarray.unit_ids,
                        "unit_labels": spiketrainarray.unit_labels,
                        "unit_tags": spiketrainarray.unit_tags,
                        "label": spiketrainarray.label}

        # initialize super so that self.fs is set:
        self._data = np.zeros((spiketrainarray.n_units,0))
            # the above is necessary so that super() can determine
            # self.n_units when initializing. self.time will
            # be updated later in __init__ to reflect subsequent changes
        super().__init__(**kwargs)

        if ds is None:
            warnings.warn('no bin size was given, assuming 62.5 ms')
            ds = 0.0625

        # TODO: this is not a good empty object to return; fix it!
        # if no tdata were received, return an empty BinnedSpikeTrain:
        if spiketrainarray.isempty:
            return BinnedSpikeTrainArray(empty=True)

        self._spiketrainarray = spiketrainarray # TODO: remove this if we don't need it, or decide that it's too wasteful
        self._support = spiketrainarray.support
        self.ds = ds

        self._bin_spikes(
            spiketrainarray=spiketrainarray,
            epochArray=self.support,
            ds=ds
            )

    def copy(self):
        """Returns a copy of the BinnedSpikeTrainArray."""
        newcopy = BinnedSpikeTrainArray(empty=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for attr in self.__attributes__:
                exec("newcopy." + attr + " = self." + attr)
        return newcopy

    def __repr__(self):
        address_str = " at " + str(hex(id(self)))
        if self.isempty:
            return "<empty BinnedSpikeTrainArray" + address_str + ">"
        ustr = " {} units in".format(self.n_units)
        if self.n_bins == 1:
            bstr = " {} bin of width {} ms".format(self.n_bins, self.ds*1000)
            dstr = ""
        else:
            bstr = " {} bins of width {} ms".format(self.n_bins, self.ds*1000)
            dstr = " for a total of {} seconds.".format(self.n_bins*self.ds)
        return "<BinnedSpikeTrainArray%s:%s%s>%s" % (address_str, ustr, bstr, dstr)

    def __iter__(self):
        """BinnedSpikeTrainArray iterator initialization."""
        # initialize the internal index to zero when used as iterator
        self._index = 0
        return self

    def __next__(self):
        """BinnedSpikeTrainArray iterator advancer."""
        index = self._index

        if index > self.support.n_epochs - 1:
            raise StopIteration

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            support = self.support[index]
            bsupport = self.binnedSupport[[index],:]

            binnedspiketrain = BinnedSpikeTrainArray(empty=True)
            exclude = ["_bins", "_data", "_support", "_centers", "_binnedSupport"]
            attrs = (x for x in self.__attributes__ if x not in exclude)
            for attr in attrs:
                exec("binnedspiketrain." + attr + " = self." + attr)
            binindices = np.insert(0, 1, np.cumsum(self.lengths + 1)) # indices of bins
            binstart = binindices[index]
            binstop = binindices[index+1]
            binnedspiketrain._bins = self._bins[binstart:binstop]
            binnedspiketrain._data = self._data[:,bsupport[0][0]:bsupport[0][1]+1]
            binnedspiketrain._support = support
            binnedspiketrain._centers = self._centers[bsupport[0][0]:bsupport[0][1]+1]
            binnedspiketrain._binnedSupport = bsupport - bsupport[0,0]
        self._index += 1
        return binnedspiketrain

    def __getitem__(self, idx):
        """BinnedSpikeTrainArray index access."""
        if isinstance(idx, EpochArray):
            if idx.isempty:
                return BinnedSpikeTrainArray(empty=True)
            if idx.fs != self.support.fs:
                support = self.support.intersect(
                    epoch=EpochArray(idx.time, fs=None),
                    boundaries=True
                    )
            else:
                support = self.support.intersect(
                    epoch=idx,
                    boundaries=True
                    ) # what if fs of slicing epoch is different?
            if support.isempty:
                return BinnedSpikeTrainArray(empty=True)
            # next we need to determine the binnedSupport:

            raise NotImplementedError("Aargh!!!")

            # with warnings.catch_warnings():
            #     warnings.simplefilter("ignore")

            #     time, tdata = self._restrict_to_epoch_array(
            #         epocharray=support,
            #         time=self.time,
            #         tdata=self.tdata,
            #         copy=True
            #         )
            #     spiketrain = SpikeTrainArray(empty=True)
            #     exclude = ["_tdata", "_time", "_support"]
            #     attrs = (x for x in self.__attributes__ if x not in exclude)
            #     for attr in attrs:
            #         exec("spiketrain." + attr + " = self." + attr)
            #     spiketrain._tdata = tdata
            #     spiketrain._time = time
            #     spiketrain._support = support
            # return spiketrain

        elif isinstance(idx, int):
            binnedspiketrain = BinnedSpikeTrainArray(empty=True)
            exclude = ["_data", "_bins", "_support", "_centers", "_spiketrainarray", "_binnedSupport"]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                attrs = (x for x in self.__attributes__ if x not in exclude)
                for attr in attrs:
                    exec("binnedspiketrain." + attr + " = self." + attr)
            support = self.support[idx]
            binnedspiketrain._support = support
            if (idx >= self.support.n_epochs) or idx < (-self.support.n_epochs):
                return binnedspiketrain
            else:
                bsupport = self.binnedSupport[[idx],:]
                centers = self.centers[bsupport[0,0]:bsupport[0,1]+1]
                binindices = np.insert(0, 1, np.cumsum(self.lengths + 1)) # indices of bins
                binstart = binindices[idx]
                binstop = binindices[idx+1]
                binnedspiketrain._data = self._data[:,bsupport[0,0]:bsupport[0,1]+1]
                binnedspiketrain._bins = self._bins[binstart:binstop]
                binnedspiketrain._binnedSupport = bsupport - bsupport[0,0]
                binnedspiketrain._centers = centers
                return binnedspiketrain
        else:  # most likely a slice
            try:
                # have to be careful about re-indexing binnedSupport
                raise NotImplementedError("Aargh222!!!")
            except Exception:
                raise TypeError(
                    'unsupported subsctipting type {}'.format(type(idx)))

    @property
    def isempty(self):
        """(bool) Empty BinnedSpikeTrainArray."""
        try:
            return len(self.centers) == 0
        except TypeError:
            return True  # this happens when self.centers == None

    @property
    def n_units(self):
        """(int) The number of units."""
        return self.data.shape[0]

    @property
    def centers(self):
        """(np.array) The bin centers (in seconds)."""
        return self._centers

    @property
    def data(self):
        """(np.array) The spike counts in all the bins.
        See also BinnedSpikeTrain.centers
        """
        return self._data

    @property
    def bins(self):
        """(np.array) The bin edges (in seconds)."""
        return self._bins

    @property
    def binnedSupport(self):
        """(np.array) The binned support of the binned spiketrain (in
        bin IDs) of shape (n_epochs, 2).
        """
        return self._binnedSupport

    @property
    def lengths(self):
        """Lenghts of contiguous segments, in number of bins."""
        return self.binnedSupport[:,1] - self.binnedSupport[:,0] + 1

    @property
    def spiketrainarray(self):
        """(nelpy.SpikeTrain) The original spiketrain associated with
        the binned data.
        """
        return self._spiketrainarray

    @property
    def n_bins(self):
        """(int) The number of bins."""
        return len(self.centers)

    @property
    def ds(self):
        """(float) Bin width in seconds."""
        return self._ds

    @ds.setter
    def ds(self, val):
        if self._ds is not None:
            raise AttributeError("can't set attribute")
        else:
            try:
                if val <= 0:
                    pass
            except:
                raise TypeError("bin width must be a scalar")
            if val <= 0:
                raise ValueError("bin width must be positive")
            self._ds = val

    @staticmethod
    def _get_bins_to_cover_epoch(epoch, ds):
        """(np.array) Return bin edges to cover an epoch."""
        # warnings.warn("WARNING! Using _get_bins_to_cover_epoch assumes " \
        #     "a starting time of 0 seconds. This is not always approapriate," \
        #     " but more flexibility is not yet supported.")
        # TODO: add flexibility to start at aritrary time
        # start = ep.start - (ep.start % ds)
        # start = ep.start - (ep.start / ds - floor(ep.start / ds))
        # because e.g., 1 % 0.1 is messed up (precision error)
        start = ds * np.floor(epoch.start / ds)
        num = np.ceil((epoch.stop - start) / ds)
        stop = start + ds * num
        bins = np.linspace(start, stop, num+1)
        centers = bins[:-1] + np.diff(bins) / 2
        return bins, centers

    def _bin_spikes(self, spiketrainarray, epochArray, ds):
        b = []  # bin list
        c = []  # centers list
        s = []  # data list
        for nn in range(spiketrainarray.n_units):
            s.append([])
        left_edges = []
        right_edges = []
        counter = 0
        for epoch in epochArray:
            bins, centers = self._get_bins_to_cover_epoch(epoch, ds)
            for uu, spiketraintimes in enumerate(spiketrainarray.time):
                spike_counts, _ = np.histogram(
                    spiketraintimes,
                    bins=bins,
                    density=False,
                    range=(epoch.start,epoch.stop)
                    ) # TODO: is it faster to limit range, or to cut out spikes?
                s[uu].extend(spike_counts.tolist())
            left_edges.append(counter)
            counter += len(centers) - 1
            right_edges.append(counter)
            counter += 1
            b.extend(bins.tolist())
            c.extend(centers.tolist())
        self._bins = np.array(b)
        self._centers = np.array(c)
        self._data = np.array(s)
        le = np.array(left_edges)
        le = le[:, np.newaxis]
        re = np.array(right_edges)
        re = re[:, np.newaxis]
        self._binnedSupport = np.hstack((le, re))

    @property
    def n_active(self):
        """Number of active units per time bin with shape (n_bins,)."""
        # TODO: profile several alternatves. Could use data > 0, or
        # other numpy methods to get a more efficient implementation:
        return self.data.clip(max=1).sum(axis=0)

    @property
    def n_spikes(self):
        """(np.array) The number of spikes in each unit."""
        if self.isempty:
            return 0
        return self.data.sum(axis=1)

    def flatten(self, *, unit_id=None, unit_label=None):
        """Collapse spike trains across units.

        WARNING! unit_tags are thrown away when flattening.

        Parameters
        ----------
        unit_id: (int)
            (unit) ID to assign to flattened spike train, default is 0.
        unit_label (str)
            (unit) Label for spike train, default is 'flattened'.
        """
        if self.n_units == 1:  # already flattened
            return self

        # default args:
        if unit_id is None:
            unit_id = 0
        if unit_label is None:
            unit_label = "flattened"

        binnedspiketrainarray = BinnedSpikeTrainArray(empty=True)

        exclude = ["_data", "unit_ids", "unit_labels", "unit_tags"]
        attrs = (x for x in self.__attributes__ if x not in "_data")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for attr in attrs:
                exec("binnedspiketrainarray." + attr + " = self." + attr)
        binnedspiketrainarray._data = np.array(self.data.sum(axis=0), ndmin=2)
        binnedspiketrainarray._unit_ids = [unit_id]
        binnedspiketrainarray._unit_labels = [unit_label]
        binnedspiketrainarray._unit_tags = None
        return binnedspiketrainarray


#----------------------------------------------------------------------#
#======================================================================#

# count number of spikes in an interval:
        # spks_bin, bins = np.histogram(st_array/fs, bins=num_bins, density=False, range=(0,maxtime))
