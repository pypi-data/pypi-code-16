# -*- coding: utf-8 -*-
import logging
import numpy as np
import os
import pandas as pd
from subprocess import check_output
import sys
import threading
from time import sleep

from enerpi.base import DATA_PATH, log
from enerpi.enerpimeter import enerpi_logger, enerpi_raw_data
from enerpi.prettyprinting import *

"""
* ENERPI Calibration utils *

Use these for:
    1. Checking electrical-net frequency (50Hz in Europe)
    2. Checking real value of voltage divisors in RMS sensing circuit schematics (without the SCT probes)
    3. Test and compare CPU usage vs sampling frequency, in order to select the optimum value for your machine.

    * Summary results for MBP:

                 CPU_mean  CPU_min  CPU_max  CPU_median  MEM_mean  MEM_min  MEM_max
    ts_data_ms
    0.00        77.420000      0.8    102.6       99.60       0.4      0.4      0.4
    0.50        32.675000      0.0     47.0       40.80       0.4      0.4      0.4
    0.75        23.096667      0.0     35.7       28.60       0.4      0.4      0.4
    1.00        13.998333      0.9     24.6       15.95       0.4      0.4      0.4
    2.00        10.510000      0.9     15.8       13.70       0.4      0.4      0.4
    3.00         7.986667      0.0     11.8       10.10       0.4      0.4      0.4
    4.00         6.986667      1.0     10.3        8.55       0.4      0.4      0.4
    5.00         5.805000      0.0      9.2        7.00       0.4      0.4      0.4
    6.00         4.811667      1.0      7.0        5.70       0.4      0.4      0.4
    7.00         4.653333      1.0      7.0        5.50       0.4      0.4      0.4
    8.00         4.345000      0.0      7.0        5.15       0.4      0.4      0.4
    9.00         3.731667      0.9      6.2        4.40       0.4      0.4      0.4
    10.00        3.478333      0.8      5.3        3.90       0.4      0.4      0.4
    11.00        3.350000      0.9      5.2        3.80       0.4      0.4      0.4
    12.00        3.193333      0.9      5.3        3.60       0.4      0.4      0.4

                 CPU_mean  CPU_min  CPU_max  CPU_median  MEM_mean  MEM_min  MEM_max
    ts_data_ms
    0.00        21.000000      0.8    105.7        1.20   0.48125  0.48125  0.48125
    0.50        26.825000      2.5     40.6       28.50   0.50000  0.50000  0.50000
    0.75        19.778125      3.4     27.4       20.60   0.50000  0.50000  0.50000
    1.00        17.768750      3.5     23.9       18.50   0.50000  0.50000  0.50000
    2.00        10.556250      2.8     13.0       11.10   0.50000  0.50000  0.50000
    3.00         7.671875      1.6     15.3        8.10   0.50000  0.50000  0.50000
    4.00         6.050000      1.6      8.6        6.15   0.50000  0.50000  0.50000
    5.00         5.403125      0.1     14.7        5.40   0.50000  0.50000  0.50000
    6.00         4.971875      0.0      6.5        5.25   0.50000  0.50000  0.50000
    7.00         4.759375      1.9      7.7        4.95   0.50000  0.50000  0.50000
    8.00         4.834375      1.9     11.9        4.60   0.50000  0.50000  0.50000
    9.00         4.071875      1.2      7.0        4.10   0.50000  0.50000  0.50000
    10.00        4.025000      1.6      7.9        4.00   0.50000  0.50000  0.50000
    11.00        3.190625      0.9      5.0        3.25   0.50000  0.50000  0.50000
    12.00        3.534375      1.4      9.5        3.40   0.50000  0.50000  0.50000
    * Summary results for RPI2:

                 CPU_mean  CPU_min  CPU_max  CPU_median  MEM_mean   MEM_min   MEM_max
    ts_data_ms
    0.00        94.865000     89.7    108.0       93.75  6.091667  6.091667  6.091667
    0.50        90.376667     87.4     93.1       90.20  7.693333  7.693333  7.693333
    0.75        87.806667     86.1     89.1       87.80  7.980000  7.980000  7.980000
    1.00        86.298333     84.7     87.3       86.30  8.725000  8.725000  8.725000
    2.00        83.155000     79.7     85.8       83.15  9.428333  9.428333  9.428333
    3.00        78.111667     74.8     80.7       78.15  9.781667  9.781667  9.781667
    4.00        73.433333     70.7     75.7       73.60  8.125000  8.125000  8.125000
    5.00        69.323333     66.9     71.4       69.40  7.895000  7.895000  7.895000
    6.00        65.856667     63.7     67.6       66.00  9.166667  9.166667  9.166667
    7.00        62.921667     61.0     64.6       63.00  9.876667  9.876667  9.876667
    8.00        60.415000     58.7     61.9       60.50  8.333333  8.333333  8.333333
    9.00        58.241667     56.7     59.5       58.40  8.673333  8.673333  8.673333
    10.00       56.336667     54.9     57.4       56.40  9.263333  9.263333  9.263333
    11.00       54.678333     53.5     55.7       54.80  9.963333  9.963333  9.963333
    12.00       53.156667     52.1     54.1       53.20  8.618333  8.618333  8.618333

                 CPU_mean  CPU_min  CPU_max  CPU_median  MEM_mean  MEM_min  MEM_max
    ts_data_ms
    0.00        52.296875     52.1     52.5       52.30       8.6      8.6      8.6
    0.50        53.200000     53.1     53.3       53.20       7.8      7.8      7.8
    0.75        53.534375     53.4     53.7       53.50       7.8      7.8      7.8
    1.00        53.531250     53.4     53.6       53.50       7.8      7.8      7.8
    2.00        53.053125     52.8     53.4       53.00       7.8      7.8      7.8
    3.00        52.290625     51.9     52.7       52.30       7.8      7.8      7.8
    4.00        51.456250     51.1     51.9       51.45       7.8      7.8      7.8
    5.00        50.568750     50.1     51.0       50.55       7.8      7.8      7.8
    6.00        49.706250     49.3     50.1       49.70       7.8      7.8      7.8
    7.00        48.859375     48.5     49.3       48.90       7.8      7.8      7.8
    8.00        48.025000     47.6     48.4       48.00       7.8      7.8      7.8
    9.00        47.231250     46.9     47.6       47.20       7.8      7.8      7.8
    10.00       46.443750     46.1     46.9       46.45       7.8      7.8      7.8
    11.00       45.690625     45.3     46.0       45.70       7.8      7.8      7.8
    12.00       44.953125     44.6     45.3       44.90       7.8      7.8      7.8


"""

PATH_ST_CALIB = os.path.join(DATA_PATH, 'raw_data_calibration.h5')
LOG_FILE_CALIB = os.path.join(DATA_PATH, 'calibration.log')


def _measure_cpu_psaux(result_data, key, ts_data_ms, interval=5, freq_s=.25):
    pid = os.getpid()
    cmd = ['ps', 'aux']
    out = check_output(cmd).decode().splitlines()
    columns = out[0].split()
    ncols = len(columns)
    idx_pid_col = columns.index('PID')
    result = []
    for i in range(interval * int(1 / freq_s)):
        out = check_output(cmd).decode().splitlines()
        result += list(map(lambda x: x.split()[:ncols - 1] + [' '.join(x.split()[ncols - 1:])],
                           filter(lambda l: l.split()[idx_pid_col] == str(pid), out[1:])))
        sleep(freq_s)
    df_ps = pd.DataFrame(result, columns=columns)
    df_ps['ts_data_ms'] = ts_data_ms
    result_data[key] = df_ps


def ascii_histogram(raw, bins=30, total_width=80):
    """
    Plot histogram in ASCII mode

    :param raw: pd.Series or pd.DataFrame with timeseries index
    :param bins: # of bins for the histogram (= nº of plot bar lines)
    :param total_width: console width
    :return: np.array with ∆T in ms

    """
    def _make_bargraph(value, label, v_max=4000, ancho_disp_bar=60):
        n_resto = 5
        v_bar = value * ancho_disp_bar / v_max
        n_big = int(v_bar)
        n_little = int(round((v_bar - int(v_bar)) / (1 / n_resto)))
        if n_little == n_resto:
            n_little = 0
            n_big += 1
        line = label + '◼︎' * n_big + '⇡︎' * n_little
        return line

    delta_ms = np.array((raw.index[1:].values - raw.index[:-1].values).astype(int) / 1e6)
    print_magenta('Histogram of ∆T sampling: min={:.3f}; max={:.3f}; mean={:.3f}; median={:.3f}'
                  .format(delta_ms.min(), delta_ms.max(), delta_ms.mean(), np.median(np.round(delta_ms, 3))))
    n_samples, ranges = np.histogram(delta_ms, bins=bins)
    max_n_samples = max(n_samples)
    mask_label = '{:.2f}->{:.2f}ms => {:5d}: '
    len_label = 10 + 2 * 3 + 5
    assert total_width - len_label > 10
    lines = [_make_bargraph(v, mask_label.format(a, b, v), v_max=max_n_samples, ancho_disp_bar=total_width - len_label)
             for v, a, b in zip(n_samples, ranges[:-1], ranges[1:])]
    for l in lines:
        print_red(l)
    return delta_ms


def _cpu_use_raw_sampling_ts(results, path_st, ts_data_ms, delta_secs=10,
                             show_histograms=False, use_dummy_sensors=True, **kwargs_logger):
    # func_enerpi_logger(results, path_st, ts_data_ms, delta_secs, show_histograms, **kwargs_logger)
    key = 'raw_ts_{}'.format(str(ts_data_ms).replace('.', '_'))
    print_secc('CPU usage (raw sampling with ∆ts = {} ms, for {} seconds)'.format(ts_data_ms, delta_secs))
    timer = threading.Thread(target=_measure_cpu_psaux, args=(results, key, ts_data_ms, delta_secs))
    timer.start()
    raw = enerpi_raw_data(path_st, key_save=key, sampling_ms=ts_data_ms, delta_secs=delta_secs,
                          use_dummy_sensors=use_dummy_sensors, **kwargs_logger)
    timer.join()
    # Raw sampling stats plots:
    if show_histograms:
        _ = ascii_histogram(raw, bins=20, total_width=120)


# noinspection PyUnusedLocal
def _cpu_use_normal_sampling_ts(results, path_st, ts_data_ms, delta_secs=10,
                                show_histograms=False, use_dummy_sensors=True, **kwargs_logger):
    # func_enerpi_logger(results, path_st, ts_data_ms, delta_secs, show_histograms, **kwargs_logger)
    key = 'rms_ts_{}'.format(str(ts_data_ms).replace('.', '_'))
    print_secc('CPU usage (raw sampling with ∆ts = {} ms, for {} seconds)'.format(ts_data_ms, delta_secs))
    timer = threading.Thread(target=_measure_cpu_psaux, args=(results, key, ts_data_ms, delta_secs))
    timer.start()
    enerpi_logger(path_st, is_demo=use_dummy_sensors, sampling_ms=ts_data_ms, timeout=delta_secs, **kwargs_logger)
    timer.join()


def _cpu_use_sampling_ts(func_enerpi_logger,
                         ts_ms_values=(0, 0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8),
                         delta_secs=10, show_histograms=True, use_dummy_sensors=True, **kwargs_logger):
    """
    Test CPU usage in raw sampling with multiple ts_data values, and summarize results

    :param ts_ms_values:
    :param delta_secs:
    :param use_dummy_sensors:
    :return: summary of test results

    """
    # CPU usage:
    results = {}
    path_st = PATH_ST_CALIB
    for ts_data_ms in ts_ms_values:
        func_enerpi_logger(results, path_st, ts_data_ms, delta_secs,
                           show_histograms, use_dummy_sensors, **kwargs_logger)
    results_ps_raw = pd.DataFrame(pd.concat(results.values())).sort_values(by='TIME')
    results_ps_raw['%CPU'] = results_ps_raw['%CPU'].apply(lambda x: float(x.replace(',', '.')))
    results_ps_raw['%MEM'] = results_ps_raw['%MEM'].apply(lambda x: float(x.replace(',', '.')))
    print_info(results_ps_raw)
    gb = results_ps_raw.groupby('ts_data_ms')
    summary = pd.concat([gb['%CPU'].mean().rename('CPU_mean'),
                         gb['%CPU'].min().rename('CPU_min'),
                         gb['%CPU'].max().rename('CPU_max'),
                         gb['%CPU'].median().rename('CPU_median'),
                         gb['%MEM'].mean().rename('MEM_mean'),
                         gb['%MEM'].mean().rename('MEM_min'),
                         gb['%MEM'].mean().rename('MEM_max')],
                        axis=1)
    print_ok(summary)
    return pd.DataFrame(summary)


def cpu_use_raw_sampling_ts(ts_ms_values=(0, 0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8),
                            delta_secs=10, use_dummy_sensors=True,
                            show_histograms=True, verbose=False):
    """
    Test CPU usage in raw sampling with multiple ts_data values, and summarize results

    :param ts_ms_values:
    :param delta_secs:
    :param use_dummy_sensors:
    :param show_histograms:
    :param verbose:
    :return: summary of test results

    """
    return _cpu_use_sampling_ts(_cpu_use_raw_sampling_ts,
                                ts_ms_values=ts_ms_values, delta_secs=delta_secs, use_dummy_sensors=use_dummy_sensors,
                                show_histograms=show_histograms, roll_time=1, verbose=verbose)


def cpu_use_normal_sampling_ts(ts_ms_values=(0, 0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8),
                               delta_secs=10, use_dummy_sensors=True):
    """
    Test CPU usage in raw sampling with multiple ts_data values, and summarize results

    :param ts_ms_values:
    :param delta_secs:
    :param use_dummy_sensors:
    :return: summary of test results

    """
    return _cpu_use_sampling_ts(_cpu_use_normal_sampling_ts,
                                ts_ms_values=ts_ms_values, delta_secs=delta_secs, use_dummy_sensors=use_dummy_sensors,
                                roll_time=1, delta_sampling=1, verbose=True)


if __name__ == '__main__':
    pd.set_option('display.width', 160)
    logging.basicConfig(filename=LOG_FILE_CALIB, level='DEBUG', datefmt='%d/%m/%Y %H:%M:%S',
                        format='%(levelname)s [%(filename)s_%(funcName)s] - %(asctime)s: %(message)s')
    is_mac = sys.platform == 'darwin'
    log('ENERPI CALIBRATION UTIL ON {}'.format('macOS' if is_mac else 'RPI'), 'magenta', True)

    # 3. Test and compare CPU usage vs sampling frequency.
    ts_test = (0, 0.5, 0.75, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)

    res_ts = cpu_use_normal_sampling_ts(ts_ms_values=ts_test, delta_secs=15, use_dummy_sensors=is_mac)
    res_ts.to_hdf(PATH_ST_CALIB, 'summary_cpu_normal')

    res_raw_ts = cpu_use_raw_sampling_ts(ts_ms_values=ts_test, delta_secs=8, use_dummy_sensors=is_mac,
                                         show_histograms=True, verbose=False)
    res_raw_ts.to_hdf(PATH_ST_CALIB, 'summary_cpu_raw')
