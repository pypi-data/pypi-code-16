#!/usr/bin/env python
# whisker_autonomic_analysis/stimulus_bp.py

"""
- Program to analyse, jointly,
  (1) "Peak" files, created like this:
        - telemetry device measuring blood pressure
        -> Spike software
        -> filter (written by Katrin Braesicke, in Spike) to remove
           non-physiological outliers
        -> text file

  (2) Stimulus timing information, either as textfile or relational database
      output from a specific Whisker task, AversivePavlovian (originally
      written by KB, then recoded by Rudolf Cardinal).

- First version: 2017-03-10.

- Note that we have no absolutely reliable way to predict "peak" file names.
  So we offer the user a manual choice, via a GUI.

- REFERENCES

[1]  https://en.wikipedia.org/wiki/Heart_rate_variability
[2]  Allen 2002
     http://apsychoserver.psych.arizona.edu/JJBAReprints/SPR2002/Allen_SPR2002.pdf
[3]  Allen
     http://apsychoserver.psych.arizona.edu/JJBAReprints/CMet/How%20to%20Reduce%20ekg%20data.htm
[4]  Toichi et al. 1997
     https://www.ncbi.nlm.nih.gov/pubmed/9021653
[5]  Lorenz 1963 "Deterministic nonperiodic flow"
     http://dx.doi.org/10.1175/1520-0469(1963)020%3C0130:DNF%3E2.0.CO;2
[6]  https://en.wikipedia.org/wiki/Poincar%C3%A9_plot
[7]  Grossman P
     https://www.researchgate.net/post/Is_there_a_standardized_method_for_measuring_vagal_tone
[8]  https://en.wikipedia.org/wiki/Unevenly_spaced_time_series
[9]  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1564191/
[10] HRV Toolkit
     https://physionet.org/tutorials/hrv-toolkit/

- TO DO:

*** Check scaling of output variables.
    For example: ln_rsa: was it expecting its IBIs in s, or ms? Etc.

*** Finish adding support for HRV Toolkit (requires extra tools that it looks for)

"""  # noqa

# Python standard library
import argparse
from datetime import datetime
import itertools
import logging
import os
import pprint
import re
import subprocess
import sys
import tempfile
import tkinter
import tkinter.filedialog
import tkinter.messagebox
from typing import Dict, Generator, List, Optional, Tuple

# Third-party imports
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
import numpy as np
from sqlalchemy.engine import Connection, create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import Column, Index
from sqlalchemy.sql.expression import text
from sqlalchemy.types import Boolean, DateTime, Float, Integer, String

# Imports from this package
from .debugging import pdb_run
from .logsupport import main_only_quicksetup_rootlogger
from .lang import auto_str, auto_repr, simple_repr
from .maths import (
    coordinates_from_x_y,
    dictminus,
    hr_bpm_from_rr_ms,
    mean,
    minus,
    rms,
    rotate_coordinates,
    rotation_matrix,
    to_db_float,
    x_y_from_coordinates,
)
from .timeseries import (
    filter_time_series,
    time_series_from_ibi,
)
from .version import VERSION, VERSION_DATE

log = logging.getLogger(__name__)
Base = declarative_base()
PlotType = PathCollection  # in case we return plots, for the type checker

# =============================================================================
# Constants
# =============================================================================

# Database field lengths
SUBJECT_NAME_LEN = 45  # as per the task
FILENAME_LEN = 255
AUTONOMIC_PARAM_LEN = 50
PHASE_LEN = 50


# =============================================================================
# Config object, to save passing around lots of configuration parameters (we
# can just pass around one).
# =============================================================================

class Config(object):
    def __init__(self,
                 connection: Optional[Connection],
                 engine: Optional[Engine],
                 hrvtk_cd_to_get_hrv: bool,
                 hrvtk_get_hrv_filename: str,
                 hrv_resample_freq_hz: float,
                 peak_dir: str,
                 rsa_low_cutoff_hz: float,
                 rsa_high_cutoff_hz: float,
                 rsa_numtaps: int,
                 sanity_checks: bool,
                 sanity_max_rr_discrepancy_s: float,
                 session: Optional[Session],
                 skip_if_results_exist: bool,
                 test_end_time_s: Optional[float],
                 test_spike_filename: str,
                 test_start_time_s: Optional[float],
                 validate: bool,
                 valid_bp_min_mmhg: float,
                 valid_bp_max_mmhg: float,
                 valid_hr_min_bpm: float,
                 valid_hr_max_bpm: float,
                 valid_max_hr_error_bpm: float,
                 validate_verbose: bool) -> None:
        self.connection = connection
        self.engine = engine
        self.hrvtk_cd_to_get_hrv = hrvtk_cd_to_get_hrv
        self.hrvtk_get_hrv_filename = hrvtk_get_hrv_filename
        self.hrv_resample_freq_hz = hrv_resample_freq_hz
        self.peak_dir = peak_dir
        self.rsa_high_cutoff_hz = rsa_high_cutoff_hz
        self.rsa_low_cutoff_hz = rsa_low_cutoff_hz
        self.rsa_numtaps = rsa_numtaps
        self.sanity_checks = sanity_checks
        self.sanity_max_rr_discrepancy_s = sanity_max_rr_discrepancy_s
        self.session = session
        self.skip_if_results_exist = skip_if_results_exist
        self.test_end_time_s = test_end_time_s
        self.test_spike_filename = test_spike_filename
        self.test_start_time_s = test_start_time_s
        self.validate = validate
        self.valid_bp_min_mmhg = valid_bp_min_mmhg
        self.valid_bp_max_mmhg = valid_bp_max_mmhg
        self.valid_hr_min_bpm = valid_hr_min_bpm
        self.valid_hr_max_bpm = valid_hr_max_bpm
        self.valid_max_hr_error_bpm = valid_max_hr_error_bpm
        self.validate_verbose = validate_verbose

        self.tempdir = tempfile.TemporaryDirectory()
        log.debug("Creating temporary directory " + repr(self.tempdir.name))
        # ... autodeleted when the object goes out of scope; see
        #     https://docs.python.org/3/library/tempfile.html
        # ... which manages it using weakref.finalize
        # ... the Config object is a nice one to have manage this scope

    def __repr__(self) -> str:
        return auto_repr(self)

    def __str__(self) -> str:
        return auto_str(self)


# =============================================================================
# Spike "peak" file format
# =============================================================================

class Heartbeat(object):
    def __init__(self,
                 cfg: Config,
                 r_time_s: float,
                 rr_interval_ms: float,
                 hr_bpm: float,
                 sbp_time_s: float,
                 sbp_mmhg: float,
                 dbp_time_s: float,
                 dbp_mmhg: float) -> None:
        """
        Class to store telemetry information, representing one row of a Spike
        "peak" file.

        :param r_time_s: time (R wave?) at which heart rate (HR) measured (s)
            ... presumably estimated somehow, since the ultimate source is a
            continuous BP trace, without ECG data.
        :param rr_interval_ms: R-R interval (= reciprocal of HR) (ms)
            a.k.a. interbeat interval (IBI)
        :param hr_bpm: HR in beats per minute
        :param sbp_time_s: time at which systolic blood pressure (SBP) measured
            (s)
        :param sbp_mmhg: SBP in millimetres of mercury
        :param dbp_time_s: time at which diastolic BP (DBP) measured (s)
        :param dbp_mmhg: DBP in millimetres of mercury

        Is the RR interval from the preceding beat, or to the next beat?
        Empirically, we check the meaning of RR interval as follows:
        (A) r_time[2] = r_time[1] + rr_interval[1]
        (B) r_time[1] = r_time[2] - rr_interval[2]

        Once three outliers are removed from the demo data set (see
        checking_rr_calcs.ods), there is nothing in it! They seem equally
        accurate (SSE_A = 0.00751689; SSE_B = 0.00758641).
        """
        self.r_time_s = r_time_s
        self.rr_interval_ms = rr_interval_ms
        self.hr_bpm = hr_bpm
        self.sbp_time_s = sbp_time_s
        self.sbp_mmhg = sbp_mmhg
        self.sbp_mmhg = sbp_mmhg
        self.dbp_time_s = dbp_time_s
        self.dbp_mmhg = dbp_mmhg
        assert r_time_s >= 0
        assert sbp_time_s >= 0
        assert dbp_time_s >= 0
        assert r_time_s < sbp_time_s < dbp_time_s
        assert cfg.valid_hr_min_bpm <= hr_bpm <= cfg.valid_hr_max_bpm
        assert cfg.valid_bp_min_mmhg <= sbp_mmhg <= cfg.valid_bp_max_mmhg
        assert cfg.valid_bp_min_mmhg <= dbp_mmhg <= cfg.valid_bp_max_mmhg
        recalc_hr = hr_bpm_from_rr_ms(rr_interval_ms)
        if abs(hr_bpm - recalc_hr) > cfg.valid_max_hr_error_bpm:
            raise ValueError(
                "hr_bpm ({}) too different from HR calculated from "
                "rr_interval_ms ({}) of {}".format(
                    hr_bpm, rr_interval_ms, recalc_hr))

    def __repr__(self) -> str:
        return simple_repr(self, ["r_time_s", "rr_interval_ms", "hr_bpm",
                                  "sbp_time_s", "sbp_mmhg",
                                  "dbp_time_s", "dbp_mmhg"])

    # Method A:
    def calc_next_beat_r_time_s(self) -> float:
        return self.r_time_s + (self.rr_interval_ms / 1000)

    # Method B:
    def calc_prev_beat_r_time_s(self) -> float:
        return self.r_time_s - (self.rr_interval_ms / 1000)

    @property
    def pulse_pressure_mmhg(self) -> float:
        return self.sbp_mmhg - self.dbp_mmhg

    @property
    def map_mmhg(self) -> float:
        """
        Calculates mean arterial pressure (MAP) as DBP + (1/3) * pulse pressure
        """
        return self.dbp_mmhg + (self.pulse_pressure_mmhg / 3)


def gen_telemetry(cfg: Config,
                  filename: str,
                  skip_initial_n_lines: int = 2,
                  end_time_marker_s: float = 10000) \
        -> Generator[Heartbeat, None, None]:
    """
    Generates TelemetryDatum items from a Spike peak file.

    :param cfg: Config object
    :param filename: filename
    :param skip_initial_n_lines: number of header lines to skip
    :param end_time_marker_s: when the time is this value, that's the
        end-of-file marker (accompanied by zero values in all other columns).
    """
    log.info("Reading Spike peak data from " + repr(filename))
    with open(filename, "r") as f:
        # http://stackoverflow.com/questions/2970780/pythonic-way-to-do-something-n-times-without-an-index-variable  # noqa
        for _ in itertools.repeat(None, skip_initial_n_lines):
            next(f)
        for line in f.readlines():
            values = [float(x) for x in line.split()]
            assert(len(values) == 8)
            assert(values[7] == 0)  # null column on the end, always 0
            if (values[0] == end_time_marker_s and
                    all(x == 0 for x in values[1:])):
                log.info("End of file marker found")
                return
            yield Heartbeat(cfg=cfg,
                            r_time_s=values[0],
                            rr_interval_ms=values[1],
                            hr_bpm=values[2],
                            sbp_time_s=values[3],
                            sbp_mmhg=values[4],
                            dbp_time_s=values[5],
                            dbp_mmhg=values[6])


def fetch_all_telemetry(cfg: Config,
                        filename: str) -> List[Heartbeat]:
    """
    Returns all the data from a Spike peak file as a list.
    """
    # noinspection PyTypeChecker
    telemetry = list(gen_telemetry(cfg, filename))  # type: List[Heartbeat]
    if cfg.sanity_checks:
        for i, heartbeat in enumerate(telemetry):
            if i == 0:  # no preceding beat
                continue
            preceding = telemetry[i - 1]
            # Is there a massive gap between heartbeats?
            # Note that some gap comes about through the removal of artefacts.
            r_discrepancy_s = abs(heartbeat.calc_prev_beat_r_time_s() -
                                  preceding.r_time_s)
            if r_discrepancy_s > cfg.sanity_max_rr_discrepancy_s:
                raise ValueError(
                    "Beat {i} [zero-numbered] has r_time_s={r_time_s}, "
                    "rr_interval_ms={rr_interval_ms}, "
                    "calc_prev_beat_r_time_s()={calc_prev_beat_r_time_s}, "
                    "but preceding beat {prec_i} has "
                    "r_time_s={prec_r_time_s} "
                    "(difference of {r_discrepancy_s} s exceeds "
                    "max permitted of {max_rr_discrepancy_s} s)".format(
                        i=i,
                        r_time_s=heartbeat.r_time_s,
                        rr_interval_ms=heartbeat.rr_interval_ms,
                        calc_prev_beat_r_time_s=heartbeat.calc_prev_beat_r_time_s(),  # noqa
                        prec_i=i - 1,
                        prec_r_time_s=preceding.r_time_s,
                        r_discrepancy_s=r_discrepancy_s,
                        max_rr_discrepancy_s=cfg.sanity_max_rr_discrepancy_s,
                    ))
            # Is the systolic BP for the preceding beat after this beat's R
            # wave? That'd be odd.
            if preceding.sbp_time_s > heartbeat.r_time_s:
                raise ValueError(
                    "Beat {prec_i} [zero-numbered] with "
                    "r_time_s={prec_r_time_s} has sbp_time={prec_sbp_time_s}, "
                    "but this is after the next beat's "
                    "r_time_s={r_time_s}".format(
                        prec_i=i - 1,
                        prec_r_time_s=preceding.r_time_s,
                        prec_sbp_time_s=preceding.sbp_time_s,
                        r_time_s=heartbeat.r_time_s,
                    ))
            # Is the diastolic BP for the preceding beat after this beat is
            # completely over? That'd be odd.
            if preceding.dbp_time_s > heartbeat.calc_next_beat_r_time_s():
                raise ValueError(
                    "Beat {prec_i} [zero-numbered] with "
                    "r_time_s={prec_r_time_s} has dbp_time={prec_dbp_time_s}, "
                    "but this is after the next beat's "
                    "calc_next_beat_r_time_s={calc_next_beat_r_time_s}".format(
                        prec_i=i - 1,
                        prec_r_time_s=preceding.r_time_s,
                        prec_dbp_time_s=preceding.dbp_time_s,
                        calc_next_beat_r_time_s=heartbeat.calc_next_beat_r_time_s,  # noqa
                    ))
    return telemetry


# =============================================================================
# External HRV analysis using HRV toolkit
# =============================================================================
# - Note: Kubios HRV is no good for this sort of thing as it doesn't seem to
#   have a command-line interface.

GET_HRV_OUTPUT = re.compile(r'(\S+)\s*=\s*(-?\d+\.?\d*)')


def get_hrv_toolkit_params(
        cfg: Config,
        ibi_values_ms: List[float],
        debug_print_file: bool = False,
        debug_wait_for_user: bool = False,
        debug_show_stdout: bool = False) -> Dict[str, float]:
    """
    Example output from get_hrv:

/tmp/tmp2yvd0lpa/tmp03tr_euy :
NN/RR    = 0.999579
AVNN     = 0.18922
SDNN     = 0.0212386
SDANN    = 0.017645
SDNNIDX  = 0.0181617
rMSSD    = 0.00863746
pNN50    = 0.00210704
    """
    if not cfg.hrvtk_get_hrv_filename:
        return {}
    if cfg.hrvtk_cd_to_get_hrv:
        hrvtk_dir = os.path.dirname(cfg.hrvtk_get_hrv_filename)
        log.debug("Changing directory to " + repr(hrvtk_dir))
        os.chdir(hrvtk_dir)
    with tempfile.NamedTemporaryFile(mode='wt', dir=cfg.tempdir.name,
                                     delete=False) as rr_file:
        rr_filename = rr_file.name
        log.debug("Writing RR data to " + repr(rr_filename))
        for ibi_ms in ibi_values_ms:
            print(ibi_ms, file=rr_file)
    # The file is now closed, but exists on disk, and we have its name.
    # Since it was created in our temporary directory, it will be cleaned up
    # when the program exits.
    if debug_print_file:
        with open(rr_filename) as f:
            for line in f:  # http://stackoverflow.com/questions/17246260
                print(line, end='')
    if debug_wait_for_user:
        input("Press Enter to continue...")
    cmdargs = [
        cfg.hrvtk_get_hrv_filename,
        '-m',  # RR intervals in ms, not s
        '-R', rr_filename,
    ]
    process = subprocess.Popen(cmdargs, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout_bin, stderr_bin = process.communicate()
    stdout = stdout_bin.decode(sys.getdefaultencoding()) if stdout_bin else ''
    stderr = stderr_bin.decode(sys.getdefaultencoding()) if stderr_bin else ''
    if stderr:
        log.warning("Error(s) from the HRV Toolkit 'get_hrv' tool:")
        log.warning(stderr)
    if debug_show_stdout:
        log.debug("Output from get_hrv:\n" + stdout)
    results = {}  # type: Dict[str, float]
    for m in GET_HRV_OUTPUT.finditer(stdout):
        try:
            param = m.group(1)
            value = float(m.group(2))
            results[param] = value
        except (TypeError, ValueError):
            pass
    log.debug("get_hrv reported: " + repr(results))
    return results


# =============================================================================
# Telemetry aggregation and calculation
# =============================================================================

class SliceBy(object):
    R_TIME = 'r_time'
    SBP_TIME = 'sbp_time'
    DBP_TIME = 'dbp_time'


def slice_telemetry(telemetry: List[Heartbeat],
                    start_time_s: float,
                    end_time_s: float,
                    slice_by: str) -> List[Heartbeat]:
    """
    Chops up a telemetry list such that all heartbeats have their time
    within the range defined by [start_time_s, end_time_s), i.e. inclusive
    for start and exclusive for end (as per Laith).

    However, there are several times associated with each heartbeat.
    Which "time" should be used? That's determined by slice_by, which can take
    values:
        'r_time'
        'sbp_time'
        'dbp_time'
    """
    # Resist the temptation to provide a default to slice_by;
    # we want users to be very clear about what they're slicing on.
    if start_time_s >= end_time_s:
        log.debug("start_time_s ({}) >= end_time_s ({})".format(
            start_time_s, end_time_s))
        return []
    if slice_by == SliceBy.R_TIME:
        return [x for x in telemetry
                if start_time_s <= x.r_time_s < end_time_s]
    elif slice_by == SliceBy.SBP_TIME:
        return [x for x in telemetry
                if start_time_s <= x.sbp_time_s < end_time_s]
    elif slice_by == SliceBy.DBP_TIME:
        return [x for x in telemetry
                if start_time_s <= x.dbp_time_s < end_time_s]
    else:
        raise ValueError("Invalid slice_by parameter")


class PoincarePlot(object):
    """
    Toichi (1997) [4] calls this a Lorenz plot, but Lorenz doesn't use it in
    the 1963 paper cited [5]; it's probably a Poincaré plot [6].
    """
    ROTATE_ANTICLOCKWISE_45 = rotation_matrix(45)
    ROTATE_CLOCKWISE_45 = rotation_matrix(-45)

    def __init__(self, intervals: np.ndarray, debug: bool = False) -> None:
        self.intervals = intervals
        self.x = intervals[:-1]  # all but the last
        self.y = intervals[1:]  # all but the first
        self.sd_longit = None
        self.sd_transverse = None
        self.toichi_l = None
        self.toichi_t = None
        self.l_line_coords = None
        self.t_line_coords = None

        if len(intervals) > 0:
            coords = coordinates_from_x_y(self.x, self.y)
            rotated_coords = rotate_coordinates(coords,
                                                self.ROTATE_ANTICLOCKWISE_45)
            transverse, longit = x_y_from_coordinates(rotated_coords)
            self.sd_longit = np.std(longit)  # type: float
            # ... this is called "SD2" by Kubios HRV
            self.sd_transverse = np.std(transverse)  # type: float
            # ... this is called "SD1" by Kubios HRV

            self.toichi_l = 4 * self.sd_longit  # [4]
            self.toichi_t = 4 * self.sd_transverse  # [4]

            mean_longit = np.mean(longit)
            mean_transverse = np.mean(transverse)
            rotated_l_coords = np.array([
                [mean_transverse, mean_longit - self.toichi_l / 2],
                [mean_transverse, mean_longit + self.toichi_l / 2]
            ])
            rotated_t_coords = np.array([
                [mean_transverse - self.toichi_t / 2, mean_longit],
                [mean_transverse + self.toichi_t / 2, mean_longit]
            ])
            self.l_line_coords = rotate_coordinates(rotated_l_coords,
                                                    self.ROTATE_CLOCKWISE_45)
            self.t_line_coords = rotate_coordinates(rotated_t_coords,
                                                    self.ROTATE_CLOCKWISE_45)

            if debug:
                log.debug("PoincarePlot.__init__:\n" + pprint.pformat({
                    'longit': longit,
                    'transverse': transverse,
                    'mean_longit': mean_longit,
                    'mean_transverse': mean_transverse,
                    'self.sd_longit': self.sd_longit,
                    'self.sd_transverse': self.sd_transverse,
                    'rotated_l_coords': rotated_l_coords,
                    'rotated_t_coords': rotated_t_coords,
                    'self.l_coords': self.l_line_coords,
                    'self.t_coords': self.t_line_coords,
                    'coords': coords,
                    'rotated_coords': rotated_coords,
                    'self.x': self.x,
                    'self.y': self.y,
                }))

    @property
    def toichi_l_over_t(self) -> Optional[float]:
        if self.toichi_l is None or self.toichi_t is None:
            return None
        return self.toichi_l / self.toichi_t

    @property
    def toichi_l_times_t(self) -> Optional[float]:
        if self.toichi_l is None or self.toichi_t is None:
            return None
        return self.toichi_l * self.toichi_t

    @property
    def sd1(self) -> float:
        # sd_transverse is called SD1 by Kubios HRV
        return self.sd_transverse

    @property
    def sd2(self) -> float:
        # sd_longit is called SD2 by Kubios HRV
        return self.sd_longit

    def plot(self) -> None:
        if self.intervals is None or len(self.intervals) == 0:
            return
        fig = plt.figure()

        tacho_x = list(range(len(self.intervals)))
        tacho_y = self.intervals
        tacho_ax = fig.add_subplot(3, 1, 1)
        tacho_ax.set_title("IBI by beat")
        tacho_ax.set_xlabel("Beat number")
        tacho_ax.set_ylabel("Interbeat_interval (ms)")
        tacho_ax.plot(tacho_x, tacho_y, 'k-')
        tacho_ax.plot(tacho_x, tacho_y, 'ro')

        rate_x = list(range(len(self.intervals)))
        rate_y = hr_bpm_from_rr_ms(self.intervals)
        rate_ax = fig.add_subplot(3, 1, 2)
        rate_ax.set_title("Calculated rate by beat")
        rate_ax.set_xlabel("Beat number")
        rate_ax.set_ylabel("HR (bpm)")
        rate_ax.plot(rate_x, rate_y, 'k-')
        rate_ax.plot(rate_x, rate_y, 'ro')

        poincare_x = self.intervals[:-1]  # all but the last
        poincare_y = self.intervals[1:]  # all but the first
        poincare_ax = fig.add_subplot(3, 1, 3)
        poincare_ax.set_title("Poincaré plot")
        poincare_ax.set_xlabel("Interbeat_interval[k] (ms)")
        poincare_ax.set_ylabel("Interbeat_interval[k+1] (ms)")
        poincare_ax.plot(poincare_x, poincare_y, 'ro')

        l_x, l_y = x_y_from_coordinates(self.l_line_coords)
        t_x, t_y = x_y_from_coordinates(self.t_line_coords)
        poincare_ax.plot(l_x, l_y, 'k-')
        poincare_ax.plot(t_x, t_y, 'k-')
        poincare_ax.text(l_x[1], l_y[1], "L")
        poincare_ax.text(t_x[1], t_y[1], "T")

        fig.gca().set_aspect('equal', adjustable='box')
        # fig.tight_layout()

        plt.show()


class CardiacIndices(object):
    PARAM_N_IBI = "n_IBI"
    PARAM_CSI = "CSI"
    PARAM_CVI = "CVI_log10_ms"
    PARAM_HRV = "HRV_ln_ms2"
    PARAM_IBI = "IBI_mean_ms"
    PARAM_MSD = "MSD_ms"
    PARAM_PNN50 = "PNN50"
    PARAM_RMSSD = "RMSSD_ms"
    PARAM_RSA = "RSA_ln_ms2"
    PARAM_SDNN = "SDNN_ms"
    PARAM_TOICHI_KUBIOS_SD1 = "Toichi_Kubios_SD1_T_ms"
    PARAM_TOICHI_KUBIOS_SD2 = "Toichi_Kubios_SD2_L_ms"
    PARAM_TOICHI_L = "Toichi_L_ms"
    PARAM_TOICHI_T = "Toichi_T_ms"

    # For details see [10]:
    PARAM_HRVTK_RMSSD = "HRVToolkit_rMSSD_s"
    # ... Square root of the mean of the squares of differences between
    #     adjacent NN intervals
    PARAM_HRVTK_PNN50 = "HRVToolkit_pNN50"
    # ... Percentage of differences between adjacent NN intervals that are
    #     greater than 50 ms; a member of the larger pNNx family
    PARAM_HRVTK_NN_RR = "HRVToolkit_NN/RR"
    # ... "NN/RR is the fraction of total RR intervals that are classified as
    #     normal-to-normal (NN) intervals and included in the calculation of
    #     HRV statistics. This ratio can be used as a measure of data
    #     reliability. For example, if the NN/RR ratio is less than 0.8, fewer
    #     than 80% of the RR intervals are classified as NN intervals, and the
    #     results will be somewhat unreliable." [10]
    PARAM_HRVTK_AVNN = "HRVToolkit_AVNN_s"  # average of all NN intervals
    PARAM_HRVTK_SDNN = "HRVToolkit_SDNN_s"  # SD of all NN intervals
    PARAM_HRVTK_SDANN = "HRVToolkit_SDANN_s"
    # ... SD of averages of NN intervals in all 5-minute segments of a 24-h
    #     recording
    PARAM_HRVTK_SDNNIDX = "HRVToolkit_SDNNIDX_s"
    # ... Mean of the SDs of NN intervals in all 5-minute segments of a 24-h
    #     recording

    VALID_PARAMETERS = [
        # Ours:
        PARAM_N_IBI,
        PARAM_CSI,
        PARAM_CVI,
        PARAM_HRV,
        PARAM_IBI,
        PARAM_MSD,
        PARAM_PNN50,
        PARAM_RMSSD,
        PARAM_RSA,
        PARAM_SDNN,
        PARAM_TOICHI_KUBIOS_SD1,
        PARAM_TOICHI_KUBIOS_SD2,
        PARAM_TOICHI_L,
        PARAM_TOICHI_T,
        # External: HRV Toolkit
        PARAM_HRVTK_RMSSD,
        PARAM_HRVTK_PNN50,
        PARAM_HRVTK_NN_RR,
        PARAM_HRVTK_AVNN,
        PARAM_HRVTK_SDNN,
        # DO NOT CARE # PARAM_HRVTK_SDANN,
        # DO NOT CARE # PARAM_HRVTK_SDNNIDX,

        # *** more to come when HRV Toolkit working properly
    ]
    _SUBTRACTABLE_ATTR_NAMES = [
        "csi",
        "cvi",
        "ln_hrv",
        "ln_rsa",
        "mean_ibi_ms",
        "msd",
        "n_ibi",
        "pnn50",
        "rmssd",
        "sdnn",
        "toichi_kubios_sd1",
        "toichi_kubios_sd2",
        "toichi_l",
        "toichi_t",
    ]
    _ATTR_NAMES = _SUBTRACTABLE_ATTR_NAMES + [
        "hrv_toolkit",
        "is_difference",
    ]

    def __init__(self,
                 cfg: Config = None,
                 ibi_values_ms: List[float] = None,
                 show_poincare_plot: bool = False,
                 show_filter_response: bool = False,
                 show_filtered_rsa: bool = False) -> None:
        self.csi = None
        self.cvi = None
        self.hrv_toolkit = {}
        self.is_difference = False
        self.ln_hrv = None
        self.ln_rsa = None
        self.mean_ibi_ms = None
        self.msd = None
        self.n_ibi = None
        self.pnn50 = None
        self.poincare_plot = None
        self.rmssd = None
        self.sdnn = None
        self.toichi_kubios_sd1 = None
        self.toichi_kubios_sd2 = None
        self.toichi_l = None
        self.toichi_t = None

        if not ibi_values_ms:
            return

        assert ibi_values_ms is not None
        assert None not in ibi_values_ms
        nn = np.array(ibi_values_ms, dtype=float)
        # ... beat-to-beat intervals are often called NN intervals [1, 2], and
        # it's a short name.
        nn_diffs = np.diff(nn, n=1)

        self.poincare_plot = PoincarePlot(nn)
        if show_poincare_plot:
            self.poincare_plot.plot()

        # ---------------------------------------------------------------------
        # Misc
        # ---------------------------------------------------------------------

        # Mean interbeat interval [2, 3]
        self.mean_ibi_ms = np.mean(nn)  # type: float

        # Mean heart rate (recalculated from IBIs) [2, 3]
        self.mean_hr_bpm = np.mean(hr_bpm_from_rr_ms(nn))

        # Toichi: Cardiac Sympathetic Index [4]
        self.csi = self.poincare_plot.toichi_l_over_t  # [4, p82]

        # Toichi L: Length of longitudinal axis [4]
        self.toichi_l = self.poincare_plot.toichi_l
        # and corresponding SD:
        self.toichi_kubios_sd2 = self.poincare_plot.sd2

        # Toichi T: Length of transverse axis [4]
        self.toichi_t = self.poincare_plot.toichi_t
        # and corresponding SD:
        self.toichi_kubios_sd1 = self.poincare_plot.sd1

        # Number of interbeat intervals [3]
        self.n_ibi = len(nn)

        # ---------------------------------------------------------------------
        # Measures of heart rate variability (both sympathetic and
        # parasympathetic influences) [3]
        # ---------------------------------------------------------------------

        # Standard deviation of IBIs [2, 3]
        self.sdnn = np.std(nn)  # type: float

        # Root-mean-square of differences between IBIs [2, 3]
        self.rmssd = rms(nn_diffs)

        abs_nn_diffs = np.abs(nn_diffs)

        # MSD: Mean of the absolute value of consecutive IBI differences [3]
        self.msd = np.mean(abs_nn_diffs)  # type: float

        # Heart rate variability
        # - affected by SNS & PNS
        # - operationalized as natural log of variance of IBI series [2, 3]
        self.ln_hrv = np.log(np.var(nn))

        # ---------------------------------------------------------------------
        # Measures of respiratory sinus arrhythmia [3]
        # ... which is not the same as vagal tone [7]
        # ---------------------------------------------------------------------

        # PNN50: Proportion of the consecutive (absolute) IBI differences
        # greater than 50 msec [3]
        def pnn(over_length_ms: int):
            n_ibi_diffs = len(abs_nn_diffs)
            n_ibi_diffs_over = len([d for d in abs_nn_diffs
                                    if d > over_length_ms])
            return n_ibi_diffs_over / n_ibi_diffs

        self.pnn50 = pnn(over_length_ms=50)

        # CVI: Toichi Cardiac Vagal Index
        self.cvi = np.log10(self.poincare_plot.toichi_l_times_t)  # [4, p. 81]

        # LogRSA: Natural Log of variance of filtered (.12-.40 Hz) IBI Series
        # [2, 9]
        ts = time_series_from_ibi(ibi_ms=nn,
                                  frequency_hz=cfg.hrv_resample_freq_hz)
        filtered = filter_time_series(
            time_series=ts,
            numtaps=cfg.rsa_numtaps,
            low_cutoff_hz=cfg.rsa_low_cutoff_hz,
            high_cutoff_hz=cfg.rsa_high_cutoff_hz,
            sampling_freq_hz=cfg.hrv_resample_freq_hz,
            show_filter_response=show_filter_response,
            show_plot=show_filtered_rsa
        )
        _, fil_y = x_y_from_coordinates(filtered)
        self.ln_rsa = np.log(np.var(fil_y))  # units: ln(ms^2)

        # ---------------------------------------------------------------------
        # External tool results
        # ---------------------------------------------------------------------

        self.hrv_toolkit = get_hrv_toolkit_params(cfg=cfg,
                                                  ibi_values_ms=ibi_values_ms)

    def __sub__(self, other: 'CardiacIndices') -> 'CardiacIndices':
        result = CardiacIndices()
        for attr in self._SUBTRACTABLE_ATTR_NAMES:
            setattr(result, attr, minus(getattr(self, attr),
                                        getattr(other, attr)))
        result.hrv_toolkit = dictminus(self.hrv_toolkit, other.hrv_toolkit)
        result.is_difference = True
        return result

    def __repr__(self) -> str:
        return simple_repr(self, self._ATTR_NAMES)

    def get_parameter(self, autonomic_parameter: str) -> float:
        if autonomic_parameter == self.PARAM_N_IBI:
            return self.n_ibi
        elif autonomic_parameter == self.PARAM_CSI:
            return self.csi
        elif autonomic_parameter == self.PARAM_CVI:
            return self.cvi
        elif autonomic_parameter == self.PARAM_HRV:
            return self.ln_hrv
        elif autonomic_parameter == self.PARAM_IBI:
            return self.mean_ibi_ms
        elif autonomic_parameter == self.PARAM_MSD:
            return self.msd
        elif autonomic_parameter == self.PARAM_PNN50:
            return self.pnn50
        elif autonomic_parameter == self.PARAM_RMSSD:
            return self.rmssd
        elif autonomic_parameter == self.PARAM_RSA:
            return self.ln_rsa
        elif autonomic_parameter == self.PARAM_TOICHI_KUBIOS_SD1:
            return self.toichi_kubios_sd1
        elif autonomic_parameter == self.PARAM_TOICHI_KUBIOS_SD2:
            return self.toichi_kubios_sd2
        elif autonomic_parameter == self.PARAM_SDNN:
            return self.sdnn
        elif autonomic_parameter == self.PARAM_TOICHI_L:
            return self.toichi_l
        elif autonomic_parameter == self.PARAM_TOICHI_T:
            return self.toichi_t
        elif autonomic_parameter == self.PARAM_HRVTK_RMSSD:
            return self.hrv_toolkit.get('rMSSD')
        elif autonomic_parameter == self.PARAM_HRVTK_PNN50:
            return self.hrv_toolkit.get('pNN50')
        elif autonomic_parameter == self.PARAM_HRVTK_NN_RR:
            return self.hrv_toolkit.get('NN/RR')
        elif autonomic_parameter == self.PARAM_HRVTK_AVNN:
            return self.hrv_toolkit.get('AVNN')
        elif autonomic_parameter == self.PARAM_HRVTK_SDNN:
            return self.hrv_toolkit.get('SDNN')
        elif autonomic_parameter == self.PARAM_HRVTK_SDANN:
            return self.hrv_toolkit.get('SDANN')
        elif autonomic_parameter == self.PARAM_HRVTK_SDNNIDX:
            return self.hrv_toolkit.get('SDNNIDX')
        else:
            raise AssertionError("Invalid parameter: " +
                                 repr(autonomic_parameter))

    def get_parameter_and_is_diff(self, autonomic_parameter: str) \
            -> Tuple[float, bool]:
        return self.get_parameter(autonomic_parameter), self.is_difference


class TelemetryMeans(object):
    PARAM_N_BEATS = "n_beats"
    PARAM_HR = "HR"
    PARAM_SBP = "SBP"
    PARAM_DBP = "DBP"
    PARAM_MAP = "MAP"

    OWN_PARAMETERS = [PARAM_N_BEATS, PARAM_HR, PARAM_SBP, PARAM_DBP, PARAM_MAP]
    VALID_PARAMETERS = OWN_PARAMETERS + CardiacIndices.VALID_PARAMETERS

    _ATTR_NAMES = [
        "cardiac_indices",
        "end_time_s",
        "is_difference",
        "mean_dbp_mmhg",
        "mean_hr_bpm",
        "mean_map_mmhg",
        "mean_sbp_mmhg",
        "n_beats",
        "start_time_s",
    ]

    def __init__(self,
                 cfg: Config = None,
                 telemetry: List[Heartbeat] = None,
                 start_time_s: float = None,
                 end_time_s: float = None,
                 show_poincare_plot: bool = False,
                 show_filter_response: bool = False,
                 show_filtered_rsa: bool = False) -> None:
        self.cardiac_indices = CardiacIndices()
        self.end_time_s = end_time_s
        self.is_difference = False
        self.mean_dbp_mmhg = None
        self.mean_hr_bpm = None
        self.mean_map_mmhg = None
        self.mean_sbp_mmhg = None
        self.n_beats = None
        self.start_time_s = start_time_s

        if not telemetry:
            return

        # Slice, or use whole series:
        if start_time_s is not None and end_time_s is not None:
            # We will slice in different ways according to the values of
            # interest:
            sliced_by_r_time = slice_telemetry(
                telemetry,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
                slice_by=SliceBy.R_TIME)
            sliced_by_sbp_time = slice_telemetry(
                telemetry,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
                slice_by=SliceBy.SBP_TIME)
            sliced_by_dbp_time = slice_telemetry(
                telemetry,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
                slice_by=SliceBy.DBP_TIME)
            hr_values_bpm = [x.hr_bpm for x in sliced_by_r_time]  # as per Laith's code  # noqa
            sbp_values_mmhg = [x.sbp_mmhg for x in sliced_by_sbp_time]  # as per Laith's code  # noqa
            dbp_values_mmhg = [x.dbp_mmhg for x in sliced_by_dbp_time]  # as per Laith's code  # noqa
            map_values_mmhg = [x.map_mmhg for x in sliced_by_sbp_time]  # as per Laith's code  # noqa
            ibi_values_ms = [x.rr_interval_ms for x in sliced_by_r_time]  # RNC
        elif start_time_s is not None or end_time_s is not None:
            raise ValueError("If you specify one of start_time_s or "
                             "end_time_s,  you must specify them both")
        else:
            assert telemetry is not None  # makes type checker happier
            hr_values_bpm = [x.hr_bpm for x in telemetry]
            sbp_values_mmhg = [x.sbp_mmhg for x in telemetry]
            dbp_values_mmhg = [x.dbp_mmhg for x in telemetry]
            map_values_mmhg = [x.map_mmhg for x in telemetry]
            ibi_values_ms = [x.rr_interval_ms for x in telemetry]

        # Calculate values
        self.cardiac_indices = CardiacIndices(
            cfg=cfg,
            ibi_values_ms=ibi_values_ms,
            show_poincare_plot=show_poincare_plot,
            show_filter_response=show_filter_response,
            show_filtered_rsa=show_filtered_rsa)
        self.n_beats = len(hr_values_bpm)
        self.mean_hr_bpm = mean(hr_values_bpm)
        self.mean_sbp_mmhg = mean(sbp_values_mmhg)
        self.mean_dbp_mmhg = mean(dbp_values_mmhg)
        self.mean_map_mmhg = mean(map_values_mmhg)

    def __repr__(self) -> str:
        return simple_repr(self, self._ATTR_NAMES)

    def __sub__(self, other: 'TelemetryMeans') -> 'TelemetryMeans':
        # For calculating differences: self - other
        result = TelemetryMeans()
        if result.cardiac_indices:
            result.cardiac_indices = (self.cardiac_indices -
                                      other.cardiac_indices)
        else:
            result.cardiac_indices = None
        result.mean_hr_bpm = minus(self.mean_hr_bpm, other.mean_hr_bpm)
        result.mean_sbp_mmhg = minus(self.mean_sbp_mmhg, other.mean_sbp_mmhg)
        result.mean_dbp_mmhg = minus(self.mean_dbp_mmhg, other.mean_dbp_mmhg)
        result.mean_map_mmhg = minus(self.mean_map_mmhg, other.mean_map_mmhg)
        result.is_difference = True
        return result

    def get_parameter(self, autonomic_parameter: str) -> float:
        if autonomic_parameter == self.PARAM_N_BEATS:
            return self.n_beats
        elif autonomic_parameter == self.PARAM_HR:
            return self.mean_hr_bpm
        elif autonomic_parameter == self.PARAM_SBP:
            return self.mean_sbp_mmhg
        elif autonomic_parameter == self.PARAM_DBP:
            return self.mean_dbp_mmhg
        elif autonomic_parameter == self.PARAM_MAP:
            return self.mean_map_mmhg
        else:
            return self.cardiac_indices.get_parameter(autonomic_parameter)

    def get_parameter_and_is_diff(self, autonomic_parameter: str) \
            -> Tuple[float, bool]:
        param = self.get_parameter(autonomic_parameter)
        if autonomic_parameter in self.OWN_PARAMETERS:
            is_difference = self.is_difference
        else:
            is_difference = self.cardiac_indices.is_difference
        return param, is_difference


# =============================================================================
# Testing Spike reading and aggregation
# =============================================================================

LOG_EQUISPACED_TEST_FREQS = [
    (0.01, 1),
    # (0.0316, 1),
    (0.1, 1),
    # (0.316, 1),
    # (1, 1),
    # (3.16, 1),
]
LINEAR_EQUISPACED_TEST_FREQS = [
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 1),
]


def test_filters(cfg: Config,
                 freq_amp_pairs: List[Tuple[float, float]],
                 sampling_freq_hz: float = None,
                 duration_s: float = 400,
                 numtaps: int = None,
                 low_cutoff_hz: float = None,
                 high_cutoff_hz: float = None,
                 show_filter_response: bool = False,
                 log_freq_in_spectrum: bool = True,
                 test_strip_last_number: bool = False,
                 debug: bool = False) -> None:
    log.info("Testing filters")

    # Filter parameters
    numtaps = numtaps or cfg.rsa_numtaps
    low_cutoff_hz = low_cutoff_hz or cfg.rsa_low_cutoff_hz
    high_cutoff_hz = high_cutoff_hz or cfg.rsa_high_cutoff_hz

    # Signal parameters
    sampling_freq_hz = sampling_freq_hz or cfg.hrv_resample_freq_hz

    # Make signal
    n = int(duration_s * sampling_freq_hz)
    assert n > 0, "No samples, with duration_s={}, sampling_freq_hz={}".format(
        duration_s, sampling_freq_hz)
    y = np.zeros(n)
    t = np.linspace(0.0, duration_s, num=n)
    for freq, amp in freq_amp_pairs:
        y += amp * np.sin(2 * np.pi * t * freq)
    if test_strip_last_number:  # e.g. check FFT with odd/even sample size
        t = t[:-1]
        y = y[:-1]
    time_series_coords = coordinates_from_x_y(t, y)

    log.info("test_filters:\n" + pprint.pformat({
        'n': n,
        'sampling_freq_hz': sampling_freq_hz,
        'duration_s': duration_s,
        'freq_amp_pairs': freq_amp_pairs,
    }))
    if debug:
        log.debug("test_filters:\n" + pprint.pformat({
            't': t,
            'y': y,
        }))

    filter_time_series(
        time_series=time_series_coords,
        numtaps=numtaps,
        low_cutoff_hz=low_cutoff_hz,
        high_cutoff_hz=high_cutoff_hz,
        sampling_freq_hz=sampling_freq_hz,
        show_filter_response=show_filter_response,
        show_plot=True,
        log_freq_in_spectrum=log_freq_in_spectrum,
    )  # result ignored


def test_spike_read(cfg: Config) -> None:
    """
    Reads all data from a Spike peak file and prints it, for testing.
    """
    filename = cfg.test_spike_filename
    log.info("Testing: reading Spike peak file {}".format(repr(filename)))
    if cfg.validate:
        telemetry = fetch_all_telemetry(cfg, filename)  # also validates
        if cfg.validate_verbose:
            for datum in telemetry:
                print(datum)
        log.info(
            "Demonstration of means for time range [{start}, {end})".format(
                start=cfg.test_start_time_s,
                end=cfg.test_end_time_s))
        info = TelemetryMeans(cfg=cfg,
                              telemetry=telemetry,
                              start_time_s=cfg.test_start_time_s,
                              end_time_s=cfg.test_end_time_s,
                              show_poincare_plot=True,
                              show_filter_response=True,
                              show_filtered_rsa=True)
        print(info)
    else:
        # noinspection PyTypeChecker
        for datum in gen_telemetry(cfg, filename):
            print(datum)


# =============================================================================
# Processing behavioural task data re CS/US timings
# =============================================================================

class SessionDefinition(object):
    def __init__(self,
                 date_time: datetime,
                 subject: str,
                 box: int,
                 peakfile_base_dir: str) -> None:
        self.date_time = date_time  # part of database PK
        self.subject = subject  # part of database PK
        self.box = box  # part of database PK
        self.peakfile_base_dir = peakfile_base_dir

    def get_peak_filename(self) -> str:
        # Ask the user!
        tkroot = tkinter.Tk()  # this has consequences; INTERACTS with pyplot
        # ... so complete and destroy Tkinter windows before returning
        tkroot.withdraw()  # prevent root window from appearing

        subject_details = "subject {s}, {dt}, box {b}".format(
            s=repr(self.subject),
            dt=self.date_time.strftime("%Y-%m-%d"),  # e.g. 2001-12-31
            b=self.box,
        )
        opentitle = "Open Spike 'peak' data file for " + subject_details
        happy = False
        filename = ''  # make type checker happy too
        while not happy:
            maybe_abort_entirely = False
            filename = tkinter.filedialog.askopenfilename(
                initialdir=self.peakfile_base_dir,
                title=opentitle,
                filetypes=(('All files', '*'),
                           ('Text files', '*.txt'))
            )
            if filename:
                result = tkinter.messagebox.askyesnocancel(
                    title="Confirm choice of Spike data file",
                    message="Use {f} for {d}?".format(f=repr(filename),
                                                      d=subject_details)
                )
                if result is None:  # Cancel
                    maybe_abort_entirely = True
                elif result:  # Yes
                    happy = True
                else:  # No
                    pass  # happy remains False
            else:
                # No filename
                maybe_abort_entirely = True
                # and happy remains False
            if maybe_abort_entirely:
                retry = tkinter.messagebox.askretrycancel(
                    title="Retry, or cancel and quit?",
                    message="Retry choosing file, or cancel program entirely?"
                )  # type: bool
                if not retry:
                    raise ValueError("User aborted program")
        tkroot.update()  # http://stackoverflow.com/questions/17575552
        tkroot.destroy()
        return filename

    def __repr__(self) -> str:
        return auto_repr(self)

    def __str__(self) -> str:
        return auto_str(self)


class TrialTiming(object):
    def __init__(self,
                 session_definition: SessionDefinition,
                 trial_number: int,
                 baseline_start_time_s: float,
                 cs_on_time_s: float,
                 cs_off_time_s: float,
                 us_on_time_s: float,
                 us_off_time_s: float) -> None:
        self.session_definition = session_definition
        self.trial_number = trial_number
        self.baseline_start_time_s = baseline_start_time_s
        self.cs_on_time_s = cs_on_time_s
        self.cs_off_time_s = cs_off_time_s
        self.us_on_time_s = us_on_time_s
        self.us_off_time_s = us_off_time_s
        # Some checks:
        try:
            assert session_definition is not None
            assert trial_number >= 0
            assert baseline_start_time_s >= 0
            assert cs_on_time_s >= baseline_start_time_s
            assert cs_off_time_s >= cs_on_time_s
            assert us_on_time_s >= cs_off_time_s
            assert us_off_time_s >= us_on_time_s
        except AssertionError:
            log.critical(pprint.pformat({
                'session_definition': session_definition,
                'trial_number': trial_number,
                'baseline_start_time_s': baseline_start_time_s,
                'cs_on_time_s': cs_on_time_s,
                'cs_off_time_s': cs_off_time_s,
                'us_on_time_s': us_on_time_s,
                'us_off_time_s': us_off_time_s,
            }))
            raise

    def __repr__(self) -> str:
        return simple_repr(self, ["trial_number", "baseline_start_time_s",
                                  "cs_on_time_s", "cs_off_time_s",
                                  "us_on_time_s", "us_off_time_s"])


class TrialTelemetryRecord(Base):
    """
    Database object, to store results.
    """
    __tablename__ = "TrialTelemetry"

    id = Column(Integer, primary_key=True)

    # FKs (non-enforced) from other tables.
    # I'm not sure that creating multiple different indexes is the best way
    # to go here... create a composite index instead (see below).
    date_time = Column(DateTime)
    subject = Column(String(length=SUBJECT_NAME_LEN))
    box = Column(Integer)
    trial = Column(Integer)

    peak_filename = Column(String(length=FILENAME_LEN))

    phase = Column(String(length=PHASE_LEN), index=True)
    start_time_s = Column(Float, nullable=True, index=True)
    end_time_s = Column(Float, nullable=True, index=True)

    autonomic_parameter = Column(String(length=AUTONOMIC_PARAM_LEN),
                                 index=True)
    parameter_value = Column(Float)
    is_difference = Column(Boolean)  # was this value created by subtraction, not measurement?  # noqa

    __table_args__ = (
        Index('idx_dt_subj_box_trial', 'date_time', 'subject', 'box', 'trial'),
    )

    def __repr__(self) -> str:
        return simple_repr(self, [
            "id", "date_time", "subject", "box", "trial",
            "peak_filename",
            "phase", "start_time", "end_time",
            "autonomic_parameter", "parameter_value", "is_difference"
        ])


class StimulusLockedTelemetry(object):
    def __init__(self,
                 telemetry: List[Heartbeat],
                 trial_timing: TrialTiming,
                 cfg: Config,
                 peak_filename: str) -> None:
        # This function is a bit inelegant; it presupposes a certain way of
        # dividing up time. This is the bit of this program that is most tied
        # to a specific behavioural task.
        # The code follows Laith's; the only generalization is chunk_s being
        # a variable (and that we don't do the same thing multiple times to
        # measure multiple variables).
        self.trial_timing = trial_timing
        self.peak_filename = peak_filename
        self.phases = {}  # Dict[str, TelemetryMeans]

        def add_directly(phase: str, tm: TelemetryMeans) -> None:
            self.phases[phase] = tm

        def add_phase(phase: str,
                      start_time_s: float,
                      end_time_s: float) -> TelemetryMeans:
            tm = TelemetryMeans(cfg=cfg,
                                telemetry=telemetry,
                                start_time_s=start_time_s,
                                end_time_s=end_time_s)
            add_directly(phase, tm)
            return tm

        chunk_s = 10  # we use 10 seconds for some calculations

        # Some of these we'll use for comparison, so make temporary copies.

        baseline = add_phase(
            'baseline',
            start_time_s=trial_timing.baseline_start_time_s,
            end_time_s=trial_timing.cs_on_time_s)
        cs = add_phase(
            'CS',
            start_time_s=trial_timing.cs_on_time_s,
            end_time_s=trial_timing.cs_off_time_s)
        us = add_phase(
            'US',
            start_time_s=trial_timing.us_on_time_s,
            end_time_s=trial_timing.us_off_time_s)

        add_phase(
            'baseline_1',
            start_time_s=trial_timing.baseline_start_time_s,
            end_time_s=trial_timing.cs_on_time_s - chunk_s)
        baseline_2 = add_phase(
            'baseline_2',
            start_time_s=trial_timing.cs_on_time_s - chunk_s,
            end_time_s=trial_timing.cs_on_time_s)

        cs_1 = add_phase(
            'CS_1',
            start_time_s=trial_timing.cs_on_time_s,
            end_time_s=trial_timing.cs_off_time_s - chunk_s)
        cs_2 = add_phase(
            'CS_2',
            start_time_s=trial_timing.cs_off_time_s - chunk_s,
            end_time_s=trial_timing.cs_off_time_s)

        us_1 = add_phase(
            'US_1',
            start_time_s=trial_timing.us_on_time_s,
            end_time_s=trial_timing.us_on_time_s + 1 * chunk_s)
        us_2 = add_phase(
            'US_2',
            start_time_s=trial_timing.us_on_time_s + 1 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 2 * chunk_s)
        us_3 = add_phase(
            'US_3',
            start_time_s=trial_timing.us_on_time_s + 2 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 3 * chunk_s)
        us_4 = add_phase(
            'US_4',
            start_time_s=trial_timing.us_on_time_s + 3 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 4 * chunk_s)
        us_5 = add_phase(
            'US_5',
            start_time_s=trial_timing.us_on_time_s + 4 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 5 * chunk_s)
        us_6 = add_phase(
            'US_6',
            start_time_s=trial_timing.us_on_time_s + 5 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 6 * chunk_s)
        us_7 = add_phase(
            'US_7',
            start_time_s=trial_timing.us_on_time_s + 6 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 7 * chunk_s)
        us_8 = add_phase(
            'US_8',
            start_time_s=trial_timing.us_on_time_s + 7 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 8 * chunk_s)
        us_9 = add_phase(
            'US_9',
            start_time_s=trial_timing.us_on_time_s + 8 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 9 * chunk_s)
        us_10 = add_phase(
            'US_10',
            start_time_s=trial_timing.us_on_time_s + 9 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 10 * chunk_s)
        us_11 = add_phase(
            'US_11',
            start_time_s=trial_timing.us_on_time_s + 10 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 11 * chunk_s)
        us_12 = add_phase(
            'US_12',
            start_time_s=trial_timing.us_on_time_s + 11 * chunk_s,
            end_time_s=trial_timing.us_on_time_s + 12 * chunk_s)

        add_directly('CS_directed', cs - baseline)
        add_directly('US_directed', us - cs)

        add_directly('CS_directed_1', cs_1 - baseline_2)
        add_directly('CS_directed_2', cs_2 - baseline_2)

        add_directly('US_directed_1', us_1 - cs_2)
        add_directly('US_directed_2', us_2 - cs_2)
        add_directly('US_directed_3', us_3 - cs_2)
        add_directly('US_directed_4', us_4 - cs_2)
        add_directly('US_directed_5', us_5 - cs_2)
        add_directly('US_directed_6', us_6 - cs_2)
        add_directly('US_directed_7', us_7 - cs_2)
        add_directly('US_directed_8', us_8 - cs_2)
        add_directly('US_directed_9', us_9 - cs_2)
        add_directly('US_directed_10', us_10 - cs_2)
        add_directly('US_directed_11', us_11 - cs_2)
        add_directly('US_directed_12', us_12 - cs_2)

    def __repr__(self) -> str:
        return auto_repr(self)

    def gen_trial_telemetry_records(self, autonomic_parameters: List[str]) \
            -> Generator[TrialTelemetryRecord, None, None]:
        tt = self.trial_timing
        sd = tt.session_definition
        for ap in autonomic_parameters:
            for phase_tm in self.phases.items():
                # Process tuple, then split, so the type checker knows...
                phase = phase_tm[0]  # type: str
                tm = phase_tm[1]  # type: TelemetryMeans
                value, is_difference = tm.get_parameter_and_is_diff(ap)
                value = to_db_float(value)
                yield TrialTelemetryRecord(
                    date_time=sd.date_time,
                    subject=sd.subject,
                    box=sd.box,

                    trial=tt.trial_number,
                    peak_filename=self.peak_filename,
                    phase=phase,

                    start_time_s=tm.start_time_s,
                    end_time_s=tm.end_time_s,
                    autonomic_parameter=ap,
                    parameter_value=value,
                    is_difference=is_difference,
                )


def fetch_trial_timings(
        connection: Connection,
        session_definition: SessionDefinition) -> List[TrialTiming]:
    # http://docs.sqlalchemy.org/en/rel_0_9/core/sqlelement.html#sqlalchemy.sql.expression.text  # noqa
    result = connection.execute(
        text("""
SELECT
    Trial,
    TrialStartTimeSec,
    CSStartTimeSec,
    CSStopTimeSec,
    USStartTimeSec,
    USStopTimeSec
FROM
    TrialRecords
WHERE
    DateTimeCode = :date_time_code
    AND Subject = :subject
    AND Box = :box
ORDER BY
    Trial
        """),
        date_time_code=session_definition.date_time,
        subject=session_definition.subject,
        box=session_definition.box,
    )
    trial_timings = []  # type: List[TrialTiming]
    for row in result:
        tt = TrialTiming(session_definition=session_definition,
                         trial_number=row['Trial'],
                         baseline_start_time_s=row['TrialStartTimeSec'],
                         cs_on_time_s=row['CSStartTimeSec'],
                         cs_off_time_s=row['CSStopTimeSec'],
                         us_on_time_s=row['USStartTimeSec'],
                         us_off_time_s=row['USStopTimeSec'])
        trial_timings.append(tt)
    return trial_timings


def delete_existing_results(dbsession: Session,
                            session_definition: SessionDefinition) -> None:
    dbsession.query(TrialTelemetryRecord).filter(
        TrialTelemetryRecord.date_time == session_definition.date_time,
        TrialTelemetryRecord.subject == session_definition.subject,
        TrialTelemetryRecord.box == session_definition.box
    ).delete()
    # See also http://stackoverflow.com/questions/39773560/sqlalchemy-how-do-you-delete-multiple-rows-without-querying  # noqa
    dbsession.commit()


def process_session(cfg: Config,
                    session_definition: SessionDefinition) -> None:
    log.info("Processing session: {}".format(session_definition))
    # Fetch data
    trial_timings = fetch_trial_timings(connection=cfg.connection,
                                        session_definition=session_definition)
    spike_peak_filename = session_definition.get_peak_filename()
    telemetry = fetch_all_telemetry(cfg, spike_peak_filename)
    # Do some thinking, and save results to the output database
    if not cfg.skip_if_results_exist:
        delete_existing_results(dbsession=cfg.session,
                                session_definition=session_definition)
    for trial_timing in trial_timings:
        log.info("... processing trial: {}".format(trial_timing))
        slt = StimulusLockedTelemetry(telemetry=telemetry,
                                      trial_timing=trial_timing,
                                      cfg=cfg,
                                      peak_filename=spike_peak_filename)
        # noinspection PyTypeChecker
        for ttr in slt.gen_trial_telemetry_records(
                autonomic_parameters=TelemetryMeans.VALID_PARAMETERS):
            cfg.session.add(ttr)
    cfg.session.commit()


def gen_session_definitions(cfg: Config) -> Generator[SessionDefinition, None,
                                                      None]:
    sql = """
SELECT
    DateTimeCode,
    Subject,
    Box
FROM
    Config AS c
    """
    if cfg.skip_if_results_exist:
        sql += """
WHERE NOT EXISTS (
    SELECT * FROM {telemetry_table} AS tt
    WHERE
        tt.date_time = c.DateTimeCode  -- both DATETIME
        AND tt.subject = c.Subject  -- both VARCHAR
        AND tt.box = c.Box  -- both INT
)
        """.format(
            telemetry_table=TrialTelemetryRecord.__tablename__,
        )
    result = cfg.connection.execute(text(sql))
    for row in result:
        yield SessionDefinition(date_time=row[0],
                                subject=row[1],
                                box=row[2],
                                peakfile_base_dir=cfg.peak_dir)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    main_only_quicksetup_rootlogger()
    thisdir = os.path.abspath(os.path.dirname(__file__))

    # Command-line arguments
    progtitle = (
        "Innes BP analysis, "
        "version {version} ({version_date}), by Rudolf Cardinal.".format(
            version=VERSION, version_date=VERSION_DATE))
    progdesc = progtitle + (
        " Takes data from (1) the database created by the AversivePavlovian "
        "Whisker behavioural task, and (2) Spike output of blood pressure "
        "telemetry data. Then (3) create stimulus-related measures of "
        "autonomic activity, and (4) stash them back in the database."
    )
    parser = argparse.ArgumentParser(
        description=progdesc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--dburl',
        help="Specify the SQLAlchemy URL to find the AversivePavlovian "
             "database",
    )
    parser.add_argument(
        '--get_hrv_filename',
        help="Specify the path to the get_hrv tool (from the HRV Toolkit, "
             "https://physionet.org/tutorials/hrv-toolkit/)",
    )
    parser.add_argument(
        '--cd_to_get_hrv', action='store_true',
        help="Change to the directory of the get_hrv tool to run it?",
    )
    parser.add_argument(
        '--no_cd_to_get_hrv', dest='cd_to_get_hrv', action='store_false',
        help="Opposite of --cd_to_get_hrv",
    )
    parser.set_defaults(cd_to_get_hrv=True)  # doesn't help under Linux; use the PATH instead  # noqa
    parser.add_argument(
        '--hrv_resample_freq_hz', type=float, default=10,
        help="Resampling frequency to create time series from interbeat "
             "intervals (IBIs), for some heart rate variability (HRV) "
             "calculations",
    )
    parser.add_argument(
        '--peakdir', default=thisdir,
        help="Specify the directory where Spike peak files live "
             "(default: %(default)s)",
    )
    parser.add_argument(
        '--rsa_low_cutoff_hz', type=float, default=0.12,
        help="High frequency cutoff for bandpass filter (amplitude is 0.5 "
             "at this frequency) for respiratory sinus arrhythmia (RSA) "
             "calculations",
    )
    parser.add_argument(
        '--rsa_high_cutoff_hz', type=float, default=0.4,
        help="Low frequency cutoff for bandpass filter (amplitude is 0.5 "
             "at this frequency) for respiratory sinus arrhythmia (RSA) "
             "calculations",
    )
    parser.add_argument(
        '--rsa_numtaps', type=int, default=241,
        help="Number of taps for the fixed-impulse-response (FIR) filter used "
             "for RSA analysis",
    )
    parser.add_argument(
        '--sanity_checks', action='store_true',
        help="Check for e.g. big gaps in telemetry during Spike file loading",
    )
    parser.add_argument(
        '--no_sanity_checks', dest='sanity_checks', action='store_false',
        help="Opposite of --sanity_checks",
    )
    parser.set_defaults(sanity_checks=True)
    parser.add_argument(
        '--sanity_max_rr_discrepancy_s', type=float, default=10,
        help="For sanity checks: maximum permitted R-R discrepancy between "
             "times of consecutive beats and stated IBI (s) "
             "(default: %(default)s)",
    )
    parser.add_argument(
        '--skip_if_results_exist', action='store_true',
        help="Skip any sessions (in the database) for which any telemetry "
             "results already exist"
    )
    parser.add_argument(
        '--no_skip_if_results_exist', action='store_false',
        dest='skip_if_results_exist',
        help="Opposite of --skip_if_results_exist: if telemetry results "
             "exist, delete existing results and redo",
    )
    parser.set_defaults(skip_if_results_exist=True)
    parser.add_argument(
        '--test_filters', action='store_true',
        help="Test filter system (then stop)",
    )
    parser.add_argument(
        '--test_spike',
        help="Specify a Spike output filename to test with (then stop)",
    )
    parser.add_argument(
        '--test_start_time_s', type=float,
        help="Start time (s) [INCLUSIVE] to analyse test Spike data (if you "
             "don't specify test_start_time_s / test_end_time_s, the whole "
             "file will be used)",
    )
    parser.add_argument(
        '--test_end_time_s', type=float,
        help="End time (s) [EXCLUSIVE] to analyse test Spike data (if you "
             "don't specify test_start_time_s / test_end_time_s, the whole "
             "file will be used)",
    )
    parser.add_argument(
        '--validate', action='store_true',
        help="Validate during Spike file loading",
    )
    parser.add_argument(
        '--no_validate', dest='validate', action='store_false',
        help="Opposite of --validate",
    )
    parser.set_defaults(validate=True)
    parser.add_argument(
        '--valid_bp_min_mmhg', type=float, default=10,
        help="For validation: minimum blood pressure (mmHg) "
             "(default: %(default)s)",
    )
    parser.add_argument(
        '--valid_bp_max_mmhg', type=float, default=300,
        help="For validation: maximum blood pressure (mmHg) "
             "(default: %(default)s)",
    )
    parser.add_argument(
        '--valid_hr_min_bpm', type=float, default=10,
        help="For validation: minimum heart rate (beats per minute) "
             "(default: %(default)s)",
    )
    parser.add_argument(
        '--valid_hr_max_bpm', type=float, default=600,  # it does go over 410!
        help="For validation: maximum heart rate (beats per minute) "
             "(default: %(default)s)",
    )
    parser.add_argument(
        '--valid_max_hr_error_bpm', type=float, default=1,
        help="For validation: maximum permissible discrepancy between heart "
             "rate stated and heart rate calculated from interbeat interval "
             "(bpm)",
    )
    parser.add_argument(
        '--validate_verbose', action='store_true',
        help="Report all data read during Spike file loading",
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help="Be verbose.",
    )
    progargs = parser.parse_args()
    log.setLevel(logging.DEBUG if progargs.verbose else logging.INFO)
    log.info(progtitle)
    log.debug("Arguments: {}".format(progargs))

    def abspath_if_given(x):
        return os.path.abspath(x) if x else ''

    db_required = not (progargs.test_filters or progargs.test_spike)

    # Create config object
    if db_required:
        # Database connection required
        if not progargs.dburl:
            raise ValueError("Database URL not specified. Try --help.")
        engine = create_engine(progargs.dburl)
        log.info("Connected to database: {}".format(engine))  # hides password
        log.info("Creating any output tables that don't exist...")
        Base.metadata.create_all(engine)
        connection = engine.connect()
        session = sessionmaker(bind=engine)()
    else:
        # No database connection required
        engine = None
        connection = None
        session = None
    cfg = Config(
        connection=connection,
        engine=engine,
        hrvtk_cd_to_get_hrv=progargs.cd_to_get_hrv,
        hrvtk_get_hrv_filename=abspath_if_given(progargs.get_hrv_filename),
        hrv_resample_freq_hz=progargs.hrv_resample_freq_hz,
        peak_dir=progargs.peakdir,
        rsa_high_cutoff_hz=progargs.rsa_high_cutoff_hz,
        rsa_low_cutoff_hz=progargs.rsa_low_cutoff_hz,
        rsa_numtaps=progargs.rsa_numtaps,
        sanity_checks=progargs.sanity_checks,
        sanity_max_rr_discrepancy_s=progargs.sanity_max_rr_discrepancy_s,
        session=session,
        skip_if_results_exist=progargs.skip_if_results_exist,
        test_end_time_s=progargs.test_end_time_s,
        test_spike_filename=abspath_if_given(progargs.test_spike),
        test_start_time_s=progargs.test_start_time_s,
        validate=progargs.validate,
        valid_bp_min_mmhg=progargs.valid_bp_min_mmhg,
        valid_bp_max_mmhg=progargs.valid_bp_max_mmhg,
        valid_hr_min_bpm=progargs.valid_hr_min_bpm,
        valid_hr_max_bpm=progargs.valid_hr_max_bpm,
        valid_max_hr_error_bpm=progargs.valid_max_hr_error_bpm,
        validate_verbose=progargs.validate_verbose,
    )
    log.info("Configuration:\n{}".format(cfg))

    # Do a test run and quit?
    if progargs.test_filters:
        test_filters(cfg, freq_amp_pairs=LOG_EQUISPACED_TEST_FREQS,
                     show_filter_response=True)
        test_filters(cfg, freq_amp_pairs=LINEAR_EQUISPACED_TEST_FREQS)
        return
    if progargs.test_spike:
        test_spike_read(cfg)
        return

    # Process all sessions found in database
    # noinspection PyTypeChecker
    log.info("Processing available sessions.")
    if cfg.skip_if_results_exist:
        log.info("... skipping any sessions for which telemetry data exists")
    count = 0
    # noinspection PyTypeChecker
    for session_definition in gen_session_definitions(cfg):
        process_session(cfg=cfg, session_definition=session_definition)
        count += 1
    log.info("All sessions processed: count = {}.".format(count))


# =============================================================================
# Command-line entry point
# =============================================================================

if __name__ == '__main__':
    with_pdb = False  # for debugging only
    if with_pdb:
        pdb_run(main)
    else:
        main()
