#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""


import datetime
import time
import collections
import json
import logging
import requests
import traceback
import copy
import usb
from data_manipulation import grl
from configparser import ConfigParser
from requests_toolbelt.multipart.encoder import MultipartEncoder

from device_drivers import usb_controller
from gateway_helpers import dt2ms, get_instrument, get_logger, post_log, \
    print_debug, round_sig


cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']

CLIENT_ID = 'ORIGINAL'
SAMPLE_FILE = 'MDO30121M.txt'
CONFIG_URL = ("https://" + COMMON_SETTINGS['DOMAIN'] + "/testplansummary/" +
              COMMON_SETTINGS['COMPANYNAME'] + '/' +
              COMMON_SETTINGS['HARDWARENAME'])
MAX_VALID_MEAS_VAL = 1e36
DEFAULT_TEK_CONFIG = {
    'acquisition': {
        'type': 'average',
        'start_time': -4.999999999999996e-06,
        'time_per_record': 9.999999999999999e-06,
        'number_of_envelopes': 0,
        'number_of_averages': 512,
        'number_of_points_minimum': 1000,
    },
    'trigger': {
        'type': 'edge',
        'source': 'ch1',
        'coupling': 'dc',
        'level': 0.288,
    },
    'trigger_edge_slope': 'positive',
    'channels': {
        'ch1': {
            'channel_enabled': True,
            'channel_offset': 0,
            'channel_range': 2,
            'channel_coupling': 'dc',
        },
        'ch2': {
            'channel_enabled': False,
            'channel_offset': 0,
            'channel_range': 1,
            'channel_coupling': 'dc',
        },
        'ch3': {
            'channel_enabled': False,
            'channel_offset': 0,
            'channel_range': 1,
            'channel_coupling': 'dc',
        },
        'ch4': {
            'channel_enabled': False,
            'channel_offset': 0,
            'channel_range': 1,
            'channel_coupling': 'dc',
        },
    },
    'outputs': {
        'enabled': False,
        'impedance': 50,
    },
    'output_noise': {
        'enabled': False,
        'percent': 0,
    },
    'standard_waveform': {
        'waveform': 'square',
        'frequency': 220000,
        'amplitude': 1,
        'dc_offset': 0,
        'duty_cycle_high': 50,
        'start_phase': 0,
        'pulse_width': 1e-06,
        'symmetry': 50,
    },
}


class Transformer(object):
    """transforms instructions from the server to instrument commands

    The Transformer will request a instrument instance based on the
    instrument_type given in the configuration and passes the parameters
    to the instrument. After the run, the Transformer reads back the data
    from the instrument to package up for a Transmitter to tranmit to
    the server."""

    def __init__(self, setup, instr=None, session=None):
        self.setup = setup
        self.instr = instr
        self.session = session

    def write_to_json_file(self, filename="sample.json", data=""):
        """Writes data out to a json file"""
        with open(filename, 'wb') as f:
            f.write(json.dumps(data))


class IviTransformer(Transformer):
    """transformer for ivi instruments"""

    def __init__(self, setup, ivi_obj, session):
        Transformer.__init__(self, setup, session=session)
        self.instr = ivi_obj


class ScopeTransformer(IviTransformer):
    """transformer for oscilloscopes"""

    def __init__(self, setup, ivi_obj=None, session=None):
        IviTransformer.__init__(self, setup, ivi_obj, session)
        self.trace_dict = {}
        self.test_run = collections.defaultdict(str, setup['test_run'])
        self.instr = ivi_obj
        self.instr._write("*CLS")
        self.channels = self.instr.channels
        self.channel_list = ['ch1', 'ch2', 'ch3', 'ch4']
        self.ch_idx_dict = {
            'ch1': 0,
            'ch2': 1,
            'ch3': 2,
            'ch4': 3,
        }
        self.enabled_list = ['ch1']  # by default, only ch1 enabled
        self.set_adders = 0
        self.exception_count = 0
        self.screenshot_blob_key = ''
        self.instrument_info = collections.defaultdict(int)
        self.g1_measurement_results = collections.defaultdict(int)
        self._horizontal_divisions = 10
        self._vertical_divisions = 10
        dd = collections.defaultdict(str)
        self.ce_dict = collections.defaultdict(lambda: dd)
        self.config_scorecard = {
            'success': [],
            'failure': [],
            'errors': {
                'usb_timeouts': 0,
                'usb_resource_busy': 0,
            },
            'times': {
                'start_to_finish': 0,
                'load_config': 0,
                'fetch_waveform': 0,
                'fetch_measurements': 0,
            }
        }
        self.times = {
            'init': time.clock(),
            'load_config_start': 0,
            'load_config_end': 0,
            'fetch_measurements_start': 0,
            'fetch_measurements_end': 0,
            'complete': 0,
        }
        self.config = collections.defaultdict(lambda: {})
        if setup['config'] == 'hybrid':
            print_debug("creating cloud capture transformer")
            self.hybrid = True
            self.config = 'hybrid'
        else:
            self.config.update(setup['config'])
            print_debug("creating user-configured transformer")
            self.hybrid = False
            try:
                ce = setup['config']['config_excerpt']
                if self.test_run['test_type'] == 'grl_test':
                    self.ce_dict.update(DEFAULT_TEK_CONFIG)
                else:
                    self.ce_dict.update(ce)
            except Exception:
                print_debug("Exception in loading Config Excerpt", post=True)
                print_debug(traceback.format_exc(), post=True)
        self.ch_index_dict = {
            'ch1': 0,
            # 'ch2': 1,
        }
        self.test_run_id = str(setup['test_run']['id'])

        if cfg.getboolean('client', 'SIMULATED'):
            self.meas_list = []
        else:
            if self.test_run['instrument_type'] == 'TektronixMSO5204B':
                self.meas_list = [
                    'rise_time',
                    'fall_time',
                    'frequency',
                    'period',
                    'voltage_rms',
                    'voltage_peak_to_peak',
                    'voltage_max',
                    'voltage_min',
                    'voltage_high',
                    'voltage_low',
                    'voltage_average',
                    'width_negative',
                    'width_positive',
                    'duty_cycle_negative',
                    'duty_cycle_positive',
                    'amplitude',
                    'voltage_cycle_rms',
                    'voltage_cycle_average',
                    'overshoot_negative',
                    'overshoot_positive',
                    # 'phase',
                    # 'delay',
                ]
            else:
                self.meas_list = [
                    'rise_time',
                    'fall_time',
                    'frequency',
                    'period',
                    'voltage_rms',
                    'voltage_peak_to_peak',
                    'voltage_max',
                    'voltage_min',
                    'voltage_high',
                    'voltage_low',
                    'voltage_average',
                    'width_negative',
                    'width_positive',
                    'duty_cycle_negative',
                    'duty_cycle_positive',
                    'amplitude',
                    'voltage_cycle_rms',
                    'voltage_cycle_average',
                    'overshoot',
                    # 'phase',
                    # 'delay',
                ]
        self.test_plan = setup['test_run']['test_plan']
        self.acq_dict = {
            'time_per_record': '',
            'number_of_points_minimum': '',
            'type': '',
            'start_time': '',
            'number_of_averages': '',
            'number_of_envelopes': '',
            'record_length': '',
        }
        try:
            self.trace_dict['more_options'] = setup[
                'test_run']['more_options_str']
        except Exception:
            print_debug("more more_options exception")

        if cfg.getboolean('client', 'SIMULATED'):
            self.ce_dict['enabled_list'] = self.enabled_list
        self.instrument_info['channels'] = []
        if self.ce_dict['channels']:
            for ch in self.ce_dict['channels']:
                self.ce_dict[ch] = self.ce_dict['channels'][ch]
        print_debug("ce_dict after init: %s" % self.ce_dict, post=True)
        try:
            print_debug("trying to get channels object")
            self.channels = self.instr.channels
            print_debug("channels found")
        except Exception:
            print_debug("EXCEPTION: unabled to get channels obj", trace=True)
            self.channels = None
        self.logfile = '/home/gradientone-admin/gateway-client/gradientone/logs/' + str(self.test_run_id) + '.log'
        self.logger = get_logger(log_filename=self.logfile)
        self.first_slice = None
        self.mid_slices = []
        self.time_step = None
        self.waveform_length = 0
        self.slice_length = 0
        self.voltage_start_time = 0  # default start_time

    def load_hybrid_config(self, try_count=0):
        print_debug("loading hybrid_config")
        ascii_config = self.config['hybrid_config'].encode('ascii')
        try:
            self.instr.system.load_setup(ascii_config)
        except Exception:
            self.logger.warning("failed loading hybrid config")
            self.logger.warning(traceback.format_exc())
            if try_count > 10:
                print_debug("not retrying")
            else:
                self.instr.close()
                time.sleep(1)
                print_debug("retrying...")
                try_count = try_count + 1
                self.instr = get_instrument(self.test_run)
                self.load_hybrid_config(try_count)

    def set_timebase(self, timebase_dict):
        for key in timebase_dict:
            self.set_adders += 1
            self._setinstr_with_tries(self.instr.timebase, key,
                                      timebase_dict[key], label='timebase_',
                                      tries=3)

    def load_config(self):
        print_debug("loading config")
        self.times['load_config_start'] = time.clock()
        if self.config['hybrid_config']:
            self.load_hybrid_config()
            time.sleep(1)

        # self.instr._interface.timeout = 100000
        if 'acquisition' in self.ce_dict:
            self._set_acquisition(self.ce_dict['acquisition'])
        if 'trigger' in self.ce_dict:
            self.set_trigger(self.ce_dict['trigger'])
        self.set_channels()
        if 'timebase' in self.ce_dict:
            self.set_timebase(self.ce_dict['timebase'])
        try:
            afg_enabled = self.ce_dict['outputs']['enabled']
            print_debug("afg_enabled is: %s" % afg_enabled, post=True)
        except Exception:
            print_debug("afg_enabled exception, setting False", post=True)
            afg_enabled = False
        if afg_enabled:
            try:
                self.set_outputs(self.ce_dict['outputs'])
                self.set_standard_waveform(self.ce_dict['standard_waveform'])
            except:
                logging.warning("AFG Enabled, but exception setting output")
        self.times['load_config_end'] = time.clock()

    def _set_acquisition(self, acq_dict):
        if 'record_length' in acq_dict:
            del acq_dict['record_length']
        print_debug("setting acquisition: " + str(acq_dict))
        try:
            if acq_dict['type'] == 'average':
                acq_dict['number_of_averages'] = int(
                    acq_dict['number_of_averages'])
            else:
                if 'number_of_averages' in acq_dict:
                    del acq_dict['number_of_averages']
            if acq_dict['type'] == 'envelope':
                acq_dict['number_of_envelopes'] = int(
                    acq_dict['number_of_envelopes'])
            else:
                if 'number_of_envelopes' in acq_dict:
                    del acq_dict['number_of_envelopes']
            if acq_dict['number_of_points_minimum']:
                acq_dict['number_of_points_minimum'] = int(
                    acq_dict['number_of_points_minimum'])
        except Exception:
            print_debug(traceback.format_exc())

        for key in acq_dict:
            self.set_adders += 1
            self._setinstr_with_tries(self.instr.acquisition, key,
                                      acq_dict[key], label='acquisition_',
                                      tries=3)

    def _setinstr_with_tries(self, ivi_obj, key, value, label='', tries=3):
        success = False
        for attempt in range(tries):
            try:
                setattr(ivi_obj, key, value)
                success = True
                break
            except usb.core.USBError as e:
                print_debug("USB Error in setting instrument", trace=True)
                self.handle_usb_error(e)
            except Exception:
                print_debug("failed to set timebase: %s %s" %
                            (key, value), trace=True)
                self.exception_count += 1
                time.sleep(0.1)
        if success:
            self.config_scorecard['success'].append(label + key)
        else:
            self.config_scorecard['failure'].append(label + key)

    def set_trigger(self, trigger_dict):
        print_debug("setting trigger")
        trigger = self.instr.trigger
        for key in trigger_dict:
            self._setinstr(trigger, key, trigger_dict[key], label='trigger_')

        if trigger_dict['type'] == 'edge':
            try:
                value = self.ce_dict['trigger_edge_slope']
                trigger.edge.slope = value
                self.config_scorecard['success'].append('trigger_edge_slope')
            except Exception:
                print_debug("failed to set edge slope with %s" % value)
                self.config_scorecard['failure'].append('trigger_edge_slope')

    def _setinstr(self, ivi_obj, key, value, label=''):
        try:
            setattr(ivi_obj, key, value)
            self.config_scorecard['success'].append(label + key)
            return True
        except Exception:
            print_debug("failed setting %s" % label + key)
            print_debug(traceback.format_exc())
            self.exception_count += 1
            self.config_scorecard['failure'].append(label + key)
            return False

    def set_standard_waveform(self, waveform_dict, index=0):
        print_debug("set standard_waveform")
        standard_waveform = self.instr.outputs[index].standard_waveform
        if not standard_waveform:
            print_debug("no standard_waveform to set")
            print_debug("outputs[0] dir: %s" % dir(self.instr.outputs[0]))
            return False

        for key in waveform_dict:
            self._setinstr(standard_waveform, key, waveform_dict[key],
                           label='standard_waveform_')
        return True

    def set_outputs(self, output_dict, index=0):
        print_debug("set outputs")
        output = self.instr.outputs[index]
        for key in output_dict:
            self._setinstr(output, key, output_dict[key], label='output_')
        try:
            output.noise.enabled = self.ce_dict['output_noise']['enabled']
            if output.noise.enabled:
                output.noise.percent = int(
                    self.ce_dict['output_noise']['percent'])
        except Exception:
            print_debug("failed to set output noise")
            print_debug(traceback.format_exc())

    def set_channels(self):
        print_debug("[DEBUG] set channels with ce_dict:%s" % self.ce_dict)
        if not self.channels:
            self.channels = self.instr.channels
        for ch in self.channel_list:
            try:
                print_debug("%s enabled: %s" %
                            (ch, self.ce_dict[ch]['channel_enabled']))
                en = self.ce_dict[ch]['channel_enabled']
                self.channels[self.ch_idx_dict[ch]].enabled = en
            except Exception:
                print_debug("exception in setting channel enabled")
            if self.channels[self.ch_idx_dict[ch]].enabled:
                self._set_channel_settings(self.channels, ch)

    def _set_channel_settings(self, channels, ch):
        channel_settings = ['offset', 'range', 'coupling', 'input_impedance']
        for setting in channel_settings:
            if setting not in self.ce_dict[ch]:
                continue
            value = self.ce_dict[ch]['channel_' + setting]
            self._setinstr(channels[self.ch_idx_dict[ch]],
                           setting,
                           value,
                           label='channel_',
                           )

    def _set_enabled_list(self):
        self.enabled_list = []  # resets enabled list
        if cfg.getboolean('client', 'SIMULATED'):
            self.enabled_list = ['ch1']
            return
        for ch in self.channel_list:
            if self.instr.channels[self.ch_idx_dict[ch]].enabled:
                self.enabled_list.append(ch)
        for ch in self.enabled_list:
            if self.config == 'hybrid':
                self.ce_dict[ch] = collections.defaultdict(int)
                self.ce_dict[ch]['channel_enabled'] = True
            elif not self.ce_dict[ch]['channel_enabled']:
                self.enabled_list.remove(ch)

    def check_commands_completed(self):
        r = self.instr._ask("*ESR?")
        self.logger.info("*ESR response: %s" % r)
        r = self.instr._ask("allev?")
        self.logger.info("allev? response: %s" % r)

    def fetch_measurements(self):
        print_debug("fetching measurements")
        self.times['fetch_measurements_start'] = time.clock()
        self._set_enabled_list()
        self.time_step = 0.000001
        self.slice_dict = collections.defaultdict(int)
        self.first_slice = collections.defaultdict(int)
        start_tse = int(dt2ms(datetime.datetime.now()))
        self.trace_dict['Start_TSE'] = start_tse  # eventually remove
        self.trace_dict['start_tse'] = start_tse  # this is better
        print_debug("enabled_list: %s" % self.enabled_list)
        meas_dict = {}
        index = 0
        for ch in self.enabled_list:
            self._fetch_waveform(ch, index, meas_dict)
            index += 1
        self._grab_and_post_screenshot()
        self._quick_post_results()
        index = 0
        self._fetch_g1_measurements()
        for ch in self.enabled_list:
            self._fetch_waveform_measurements(ch, meas_dict)
            index += 1
        self.trace_dict['raw_sec_btw_samples'] = self.time_step
        stop_tse = int(dt2ms(datetime.datetime.now()))
        self.trace_dict['Stop_TSE'] = stop_tse
        self.times['fetch_measurements_end'] = time.clock()
        return meas_dict

    def _fetch_g1_measurements(self):
        if self.test_run['g1_measurement'] == 'I2C':
            # trigger the appropriate analysis handler
            _response = requests.get("https://" + COMMON_SETTINGS["DOMAIN"] +
                                     "/analysis",
                                     params={"test_run_id": self.test_run_id,
                                             "suite": "skywave"})
            expected_result = "[\"/markers?test_run_id="+str(
                self.test_run_id)+"\", \"/get_all_meta_data/"+str(
                self.test_run_id)+"\"]"
            assert _response.status_code == 200
            assert _response.text == expected_result

    def _fetch_waveform(self, ch, index, meas_dict):
        self.check_commands_completed()
        voltage_list = None
        start_time = 0
        end_time = 0
        try:
            if cfg.getboolean('client', 'SIMULATED'):
                self.ce_dict[ch]['channel_enabled'] = True
            print_debug("%s channel_enabled: %s" %
                        (ch, self.ce_dict[ch]['channel_enabled']))
            if self.ce_dict[ch]['channel_enabled']:
                channel = self.instr.channels[self.ch_idx_dict[ch]]
                waveform = list(channel.measurement.fetch_waveform())
                print_debug("waveform length for %s: %s" %
                            (ch, len(waveform)), post=True)
                self.waveform_length = len(waveform)
                start_time = waveform[0][0]
                end_time = waveform[-1][0]
                self.time_step = waveform[1][0] - start_time
                voltage_list = self.get_voltage_list(waveform)
                slice_list = self.get_slice_list(voltage_list)
                self.slice_dict[ch] = slice_list
                self.first_slice[ch] = slice_list[0]
                mid = len(slice_list) / 2
                self.mid_slices = slice_list[mid - 1:mid + 1]
                self.check_commands_completed()
            meas_dict[ch] = collections.defaultdict(str)
            self.trace_dict[ch + '_voltages'] = voltage_list
            self.trace_dict[ch + '_start_time'] = start_time
            self.trace_dict[ch + '_end_time'] = end_time
            self.voltage_start_time = start_time  # default start_time
        except Exception:
            self.logger.warning("failed to fetch waveform for: %s" % ch)
            self.logger.warning(traceback.format_exc())

    def _fetch_waveform_measurements(self, ch_str, meas_dict):
        self.check_commands_completed()
        print_debug("fetching waveform measurements")
        if not self.channels:
            channel = self.instr.channels[ch_str]
        else:
            channel = self.channels[ch_str]
        meas_dict[ch_str]['valid'] = True
        print('the channel is:  ', channel)
        for meas in self.meas_list:

            if cfg.getboolean('client', 'SIMULATED'):
                meas_dict[ch_str][str(meas)] = "Simulated m_val"
                continue

            m_val = ''
            measurement = channel.measurement
            try:
                m_val = measurement.fetch_waveform_measurement(meas)
                print('the measurement is:  ', meas)
                self.check_commands_completed()
                meas_dict[ch_str][str(meas)] = m_val
                if m_val > MAX_VALID_MEAS_VAL:
                    meas_dict[ch_str]['valid'] = False
            except Exception:
                print_debug(ch_str + " measurement exception")
                print_debug(traceback.format_exc())

    def fetch_config_info(self, last_try=False):
        if cfg.getboolean('client', 'SIMULATED'):
            return "simulated config info"
        print_debug("fetching config_info")
        try:
            config_info = self.instr.system.fetch_setup()
        except Exception:
            self.logger.warning("fetch setup failed")
            self.logger.warning(traceback.format_exc())
            if last_try:
                return None
            else:
                config_info = self.fetch_config_info(last_try=True)
        return config_info

    def get_trigger(self):
        print_debug("getting trigger")
        trigger_dict = {
            'type': '',
            'coupling': '',
            'source': '',
            'level': '',
        }
        for name in trigger_dict:
            trigger_dict[name] = getattr(self.instr.trigger, name)
        self.ce_dict['trigger_edge_slope'] = self.instr.trigger.edge.slope
        return trigger_dict

    def get_acquisition(self):
        print_debug("getting acquisition")
        for key in self.acq_dict:
            self.acq_dict[key] = getattr(self.instr.acquisition, key)
        return self.acq_dict

    def get_standard_waveform(self, index=0):
        print_debug("getting standard_waveform")
        standard_waveform = self.instr.outputs[index].standard_waveform
        std_wave_dict = {
            'waveform': '',
            'frequency': '',
            'amplitude': '',
            'dc_offset': '',
            'duty_cycle_high': '',
            'start_phase': '',
            'pulse_width': '',
            'symmetry': '',
        }
        if standard_waveform:
            for key in std_wave_dict:
                std_wave_dict[key] = getattr(standard_waveform, key)
        else:
            print_debug("no standard_waveform object")
            print_debug("outputs[0] dir: %s" % dir(self.instr.outputs[0]))

    def get_outputs(self, index=0):
        print_debug("getting outputs")
        outputs = None
        try:
            outputs = self.instr.outputs[index]
        except Exception:
            print_debug("getting outputs exception")
        output_dict = {
            'impedance': '',
            'enabled': '',
        }
        if not outputs:
            return output_dict

        for key in output_dict:
            output_dict[key] = getattr(outputs, key)
            print_debug("output from instr: %s %s" % (key, output_dict[key]))
        output_dict['standard_waveform'] = self.get_standard_waveform()
        self.ce_dict['outputs_noise_percent'] = outputs.noise.percent
        return output_dict

    def _get_excerpt_channel_data(self):
        """updates config exerpt to match instrument reported channel enabled,
           offset, range, and coupling. Updates enabled list to match
           instrument reported enabled channels. Returns copy of updated
           config excerpt"""
        print_debug("updating config_excerpt, requesting channels")
        if not self.channels:
            self.channels = self.instr.channels
        config_excerpt = copy.deepcopy(self.ce_dict)
        self.enabled_list = []
        for ch in self.channel_list:
            if ch == "ch1" or ch == "ch2":
                ch_dict = collections.defaultdict(str)
                print_debug("requesting channel enabled data for %s" % ch)
                ch_dict['channel_enabled'] = self.channels[
                    self.ch_idx_dict[ch]].enabled
                time.sleep(0.25)
                if ch_dict['channel_enabled']:
                    print_debug("response %s enabled" % ch)
                    ch_dict['channel_offset'] = self.channels[
                        self.ch_idx_dict[ch]].offset
                    time.sleep(0.25)
                    ch_dict['channel_range'] = self.channels[
                        self.ch_idx_dict[ch]].range
                    time.sleep(0.25)
                    ch_dict['channel_coupling'] = self.channels[
                        self.ch_idx_dict[ch]].coupling
                    time.sleep(0.25)
                    cii = self.channels[self.ch_idx_dict[ch]].input_impedance
                    time.sleep(0.25)
                    ch_dict['channel_input_impedance'] = cii
                    self.enabled_list.append(ch)
                else:
                    print_debug("response: %s NOT enabled" % ch)
                config_excerpt[ch] = ch_dict
        # sync up excerpt list with transformer list
        self.ce_dict['enabled_list'] = self.enabled_list
        config_excerpt['enabled_list'] = self.enabled_list
        return config_excerpt

    def get_config_excerpt(self):
        print_debug("Pre getconfig outputs: %s" %
                    self.ce_dict['outputs'], post=True)
        if cfg.getboolean('client', 'SIMULATED'):
            return DEFAULT_TEK_CONFIG
        print_debug("getting config_excerpt")
        config_excerpt = self._get_excerpt_channel_data()
        config_excerpt['trigger'] = self.get_trigger()
        config_excerpt['acquisition'] = self.get_acquisition()
        config_excerpt['outputs'] = self.get_outputs()
        config_excerpt['timebase'] = self.get_timebase()

        return config_excerpt

    def get_timebase(self):
        timebase = collections.defaultdict(int)
        try:
            timebase['position'] = self.instr.timebase.position
        except Exception:
            print_debug("get timebase position exception")
        return timebase

    def get_probe_ids(self, total_channels=2):
        print_debug("getting probe_ids")
        probe_ids = []
        if not self.channels:
            self.channels = self.instr.channels
        for i in range(total_channels):
            probe_ids.append(self.channels[i].probe_id)
        return probe_ids

    def get_voltage_list(self, waveform):
        print_debug("getting voltage_list")
        voltage_list = [round_sig(float(point[1])) for point in waveform]
        return voltage_list

    def get_slice_list(self, voltage_list):
        """create list of slices sets class attribute"""
        print_debug("getting slice_list")
        if len(voltage_list) >= int(CLIENT_SETTINGS["MAX_LENGTH_FOR_BROWSER"]):
            slice_list = [voltage_list[x:x + int(CLIENT_SETTINGS["MAX_LENGTH_FOR_BROWSER"])]  # nopep8
                          for x in range(0, len(voltage_list), int(CLIENT_SETTINGS["MAX_LENGTH_FOR_BROWSER"]))]  # nopep8
        else:
            slice_list = [voltage_list]
        return slice_list

    def _grab_and_post_screenshot(self):
        if cfg.getboolean('client', 'SIMULATED'):
            return
        png = self.instr.display.fetch_screenshot()
        self.logger.info("_grab_and_post_screenshot")
        filename = "screenshot" + ':' + str(self.test_run_id)

        with open('tempfile.png', 'w') as f:
            self.png_file = f.write(png)
        f.close()
        self.logger.info("closed png file")

        multipartblob = MultipartEncoder(
            fields={
                'field0': (filename, open('tempfile.png', 'rb'), 'text/plain'),
                'field1': str(self.test_run_id),
            }
        )

        blob_url = requests.get("https://" + COMMON_SETTINGS["DOMAIN"] +
                                "/upload/geturl")
        response = requests.post(blob_url.text, data=multipartblob,
                                 headers={
                                    'Content-Type': multipartblob.content_type
                                    })
        print_debug("transmitblob response.reason: %s" % response.reason)
        self.logger.info("transmitblob response.status_code: %s" %
                         response.status_code)
        self.screenshot_blob_key = response.text
        self.trace_dict['screenshot_blob_key'] = response.text
        self.logger.info("screenshot_blob_key: %s" % self.screenshot_blob_key)
        self.logger.info(self.screenshot_blob_key)

    def _quick_post_results(self):
        """ post_creation_data function sends a json object
           for the browser to plot
        """
        if self.hybrid:
            config_name = str(self.test_run_id)
        else:
            config_name = self.config['name']
        self._set_divisions()
        if self.slice_dict:
            slice_list_len = len(self.slice_dict.itervalues().next())
        else:
            slice_list_len = 0
        quick_results = {
            'test_results': self.first_slice,
            'num_of_slices': slice_list_len,
            'time_step': self.time_step,
            'voltage_start_time': self.voltage_start_time,
            'test_plan': self.test_plan,
            'config_name': config_name,
            'screenshot_blob_key': self.screenshot_blob_key,
            'instrument_info': self.get_instrument_info(),
            'mid_slices': self.mid_slices,
            'total_points': self.waveform_length,
            'slice_length': len(self.first_slice),
        }
        url_t = "https://" + \
            COMMON_SETTINGS["DOMAIN"] + \
                "/tektronixdata/" + str(self.test_run_id)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        json_data = json.dumps(quick_results, ensure_ascii=True)
        response = self.session.post(url_t, data=json_data, headers=headers)
        self.logger.info("_quick_post_results response.status_code: %s"
                         % response.status_code)

    def _set_divisions(self, h_divs=0, v_divs=0):
        if self.instr._horizontal_divisions:
            self._horizontal_divisions = self.instr._horizontal_divisions
        else:
            self._horizontal_divisions = 10
        if self.instr._vertical_divisions:
            self._vertical_divisions = self.instr._vertical_divisions
        else:
            self._vertical_divisions = 8
        if h_divs:
            self._horizontal_divisions = h_divs
        if v_divs:
            self._vertical_divisions = v_divs
        self.trace_dict['h_divs'] = self._horizontal_divisions
        self.trace_dict['v_divs'] = self._vertical_divisions

    def get_horizontal_divisions(self):
        if self._horizontal_divisions:
            return self._horizontal_divisions
        else:
            self._set_divisions()
            return self._horizontal_divisions

    def get_vertical_divisions(self):
        if self._vertical_divisions:
            return self._vertical_divisions
        else:
            self._set_divisions()
            return self._vertical_divisions

    def get_instrument_info(self):
        instr_info = {'channels': []}
        instr_info['h_divs'] = self.get_horizontal_divisions()
        instr_info['v_divs'] = self.get_vertical_divisions()
        instr_info['timebase_range'] = self.instr.timebase.range
        instr_info['timebase_position'] = self.instr.timebase.position
        instr_info['timebase_scale'] = self.instr.timebase.scale
        if not self.channels:
            self.channels = self.instr.channels
        ch_counter = 0
        for ch in self.enabled_list:
            channel_info = {}
            try:
                channel_info['trigger_level'] = self.channels[
                    self.ch_idx_dict[ch]].trigger_level
            except Exception:
                post_log("exception in getting trigger_level...%s"
                         % traceback.format_exc())
            try:
                channel_info['name'] = ch
                channel_info['range'] = self.channels[
                    self.ch_idx_dict[ch]].range
                channel_info['coupling'] = self.channels[
                    self.ch_idx_dict[ch]].coupling
                channel_info['offset'] = self.channels[
                    self.ch_idx_dict[ch]].offset
                channel_info['scale'] = self.channels[
                    self.ch_idx_dict[ch]].scale
            except Exception:
                post_log("exception with range, coupling, or offset...%s"
                         % traceback.format_exc())
            instr_info['channels'].append(channel_info)
            ch_counter += 1
        # update current objects's info
        self.instrument_info.update(instr_info)
        return instr_info

    def post_status_update(self, status):
        status_url = ('https://' + COMMON_SETTINGS["DOMAIN"] + '/status/' +
                      COMMON_SETTINGS['COMPANYNAME'] + '/' +
                      COMMON_SETTINGS['HARDWARENAME'])
        self.session.post(status_url, status)

    def handle_usb_error(self, e):
        if e.args == ('Operation timed out',):
            print_debug("Found USBError: Operation timed out")
            self.config_scorecard['errors']['usb_timeouts'] += 1
        elif e.args == ('Resource busy',):
            print_debug('Found USBError: Resource busy')
            self.post_status_update(self.session, "Critical USBError")
            self.post_alert({'usb_error': 'Resource Busy'})
            self.config_scorecard['errors']['usb_resource_busy'] += 1
        else:
            print_debug('Unknown USBError')

    def update_scorecard_times(self):
        times = self.times
        stf = times['complete'] - times['init']
        lc = times['load_config_end'] - times['load_config_start']
        fm = times['fetch_measurements_end'] - \
            times['fetch_measurements_start']
        config_times = {
            'start_to_finish': stf,
            'load_config': lc,
            'fetch_measurements': fm,
        }
        self.config_scorecard['times'] = config_times


class TransformerMSO5204B(ScopeTransformer):

    def __init__(self, setup, ivi_obj, session):
        ScopeTransformer.__init__(self, setup, ivi_obj, session)
        self.channel_list = ['ch1', 'ch2', 'ch3', 'ch4']
        self.acq_dict = {
            'time_per_record': '',
            'number_of_points_minimum': '',
            'type': '',
            'start_time': '',
            'number_of_averages': '',
            'number_of_envelopes': '',
            'record_length': '',
            'sample_rate': '',
        }


    def load_config(self):
        print_debug("loading config")
        self.times['load_config_start'] = time.clock()
        if self.config['hybrid_config']:
            self.load_hybrid_config()
            time.sleep(1)

        if 'horizontal' in self.ce_dict:
            self._set_horizontal(self.ce_dict['horizontal'], self.ce_dict['acquisition'])
        if 'acquisition' in self.ce_dict:
            self._set_acquisition(self.ce_dict['acquisition'], self.ce_dict['horizontal'])
        if 'trigger' in self.ce_dict:
            self.set_trigger(self.ce_dict['trigger'])
        self.set_channels()
        print 'the dict', self.ce_dict
        if 'timebase' in self.ce_dict:
            print "setting timebase"
            self.set_timebase(self.ce_dict['timebase'])

        try:
            afg_enabled = self.ce_dict['outputs']['enabled']
            print_debug("afg_enabled is: %s" % afg_enabled, post=True)
        except Exception:
            print_debug("afg_enabled exception, setting False", post=True)
            afg_enabled = False
        if afg_enabled:
            try:
                self.set_outputs(self.ce_dict['outputs'])
                self.set_standard_waveform(self.ce_dict['standard_waveform'])
            except:
                logging.warning("AFG Enabled, but exception setting output")
        self.times['load_config_end'] = time.clock()

    def _set_acquisition(self, acq_dict, horiz_dict):
        if 'record_length' in acq_dict:
            del acq_dict['record_length']
        print_debug("setting acquisition: " + str(acq_dict))
        try:
            if acq_dict['type'] == 'average':
                acq_dict['number_of_averages'] = int(
                    acq_dict['number_of_averages'])
            else:
                if 'number_of_averages' in acq_dict:
                    del acq_dict['number_of_averages']
            if acq_dict['type'] == 'envelope':
                acq_dict['number_of_envelopes'] = int(
                    acq_dict['number_of_envelopes'])
            else:
                if 'number_of_envelopes' in acq_dict:
                    del acq_dict['number_of_envelopes']
            if acq_dict['number_of_points_minimum']:
                acq_dict['number_of_points_minimum'] = int(
                    acq_dict['number_of_points_minimum'])
                del acq_dict['number_of_points_minimum']
            if horiz_dict['sample_rate']:
                acq_dict['sample_rate'] = self._sample_rate_lookup(
                    horiz_dict['sample_rate'])

        except Exception:
            print_debug(traceback.format_exc())

        for key in acq_dict:
            self.set_adders += 1

            self._setinstr_with_tries(self.instr.acquisition, key,
                                      acq_dict[key], label='acquisition_',
                                      tries=3)
            if key == 'number_of_points_minimum':
                pass
            else:
                self._setinstr_with_tries(self.instr.acquisition, key,
                                          acq_dict[key], label='acquisition_',
                                          tries=3)


    def get_config_excerpt(self):
        print_debug("Pre getconfig outputs: %s" %
                    self.ce_dict['outputs'], post=True)
        if cfg.getboolean('client', 'SIMULATED'):
            return DEFAULT_TEK_CONFIG
        print_debug("getting config_excerpt")
        config_excerpt = self._get_excerpt_channel_data()
        config_excerpt['trigger'] = self.get_trigger()
        config_excerpt['acquisition'] = self.get_acquisition()
        config_excerpt['outputs'] = self.get_outputs()
        config_excerpt['timebase'] = self.get_timebase()
        return config_excerpt

    def get_timebase(self):
        timebase = collections.defaultdict(int)
        try:
            timebase['position'] = self.instr.timebase.position
        except Exception:
            print_debug("get timebase position exception")
        try:
            timebase['scale'] = self.instr.timebase.scale
        except Exception:
            print_debug("get timebase scaleexception")
        return timebase

        for key in horiz_dict:
            if key == 'mode':
                self.set_adders += 1
                self._setinstr_with_tries(self.instr.acquisition, key,
                                          horiz_dict[key], label='acquisition_horizontal_',
                                          tries=3)
            elif key == 'scale':
                self.set_adders += 1
                self._setinstr_with_tries(self.instr.timebase, key,
                                          horiz_dict[key], label='timebase_',
                                          tries=3)
            else:
                pass
            if key == 'number_of_points_minimum':
                pass
            else:
                self._setinstr_with_tries(self.instr.acquisition, key,
                                          acq_dict[key], label='acquisition_',
                                          tries=3)


    def get_config_excerpt(self):
        print_debug("Pre getconfig outputs: %s" %
                    self.ce_dict['outputs'], post=True)
        if cfg.getboolean('client', 'SIMULATED'):
            return DEFAULT_TEK_CONFIG
        print_debug("getting config_excerpt")
        config_excerpt = self._get_excerpt_channel_data()
        config_excerpt['trigger'] = self.get_trigger()
        config_excerpt['acquisition'] = self.get_acquisition()
        config_excerpt['outputs'] = self.get_outputs()
        config_excerpt['timebase'] = self.get_timebase()

        return config_excerpt

    def get_timebase(self):
        timebase = collections.defaultdict(int)
        try:
            timebase['position'] = self.instr.timebase.position
        except Exception:
            print_debug("get timebase position exception")
        try:
            timebase['scale'] = self.instr.timebase.scale
        except Exception:
            print_debug("get timebase scaleexception")
        return timebase


    # def set_timebase(self, timebase_dict, horiz_dict):

    #     try:
    #         if horiz_dict['scale']:
    #             timebase_dict['scale'] = self._scale_lookup(horiz_dict['scale'])
    #     except Exception:
    #         print_debug(traceback.format_exc())
    #     for key in timebase_dict:
    #         self.set_adders += 1
    #         self._setinstr_with_tries(self.instr.timebase, key,
    #                                   timebase_dict[key], label='timebase_',
    #                                   tries=3)

    def _sample_rate_lookup(self, value):
        sample_rate_table = {"400GS/s":400e9,
                            "200GS/s":200e9,
                            "80GS/s":80e9,
                            "40GS/s":40e9,
                            "20GS/s":20e9,
                            "10GS/s":10e9,
                            "5GS/s":5e9,
                            "2.5GS/s":2.5e9,
                            "1GS/s":1e9,
                            "500MS/s":500e6, 
                            "200MS/s":200e6,
                            "100MS/s":100e6,
                            "50MS/s":50e6,
                            "20MS/s":20e6,
                            "10MS/s":10e6,
                            "5MS/s":5e6,
                            "2MS/s":2e6,
                            "1MS/s":1e6,
                            "500Ks/s":500000,
                            "200Ks/s":200000,
                            "100Ks/s":100000,
                            "50Ks/s":50000,
                            "20Ks/s":20000,
                            "10Ks/s":10000,
                            "5kS/s":5000,
                            "2kS/s":2000,
                            "1kS/s":1000,
                            "500S/s":500,
                            "200S/s":200,
                            "100S/s":100,
                            "50S/s":50,
                            "20S/s":20,
                            "10S/s":10,
                            "5S/s": 5}
        sample_rate = sample_rate_table[value]
        print 'value = ', value, 'sample_rate = ', sample_rate
        return sample_rate


    def _scale_lookup(self, value):
        value = value[0]
        scale_table = {"1ks": 1000,
            "500s": 500, 
            "200s": 200, 
            "100s": 100,
            "50s": 50, 
            "20s": 20,
            "10s": 10,
            "5s": 5,
            "2s": 2,
            "1s": 1, 
            "500ms": 0.5,
            "200ms": 0.2,
            "100ms": 0.1,
            "50ms": 0.05,
            "20ms": 0.02,
            "10ms": 0.01,
            "5ms": 0.005,
            "2ms": 0.002,
            "1ms": 0.001,
            "500us": 5e-4,
            "200us": 2e-4,
            "100us": 1e-4,
            "50us": 5e-5,
            "20us": 2e-5,
            "10us": 1e-5,
            "5us": 5e-6,
            "2us": 2e-6, 
            "1us":   1e-6,
            "500ns": 5e-7,
            "200ns": 2e-7, 
            "100ns": 1e-7,
            "50ns":  5e-8,
            "20ns":  2e-8, 
            "10ns":  1e-8,
            "5ns":   5e-9,
            "2.5ns": 2.5e-9,
            "1ns":   1e-9,
            "500ps": 5e-10,
            "250ps": 2.5e-10}
        scale = scale_table[value]
        print 'value = ', value, 'scale = ', scale
        return scale

class TransformerMDO3012(ScopeTransformer):

    def __init__(self, setup, ivi_obj, session):
        ScopeTransformer.__init__(self, setup, ivi_obj, session)
        self.channel_list = ['ch1', 'ch2']

    def _set_divisions(self, v_divs=8, h_divs=10):
        self._vertical_divisions = v_divs
        self._horizontal_divisions = h_divs


class TransformerMSO2024(ScopeTransformer):
    """overrides get_config_excerpt to skip outputs"""

    def get_config_excerpt(self):
        config_excerpt = self._get_excerpt_channel_data()
        config_excerpt['trigger'] = self.get_trigger()
        config_excerpt['acquisition'] = self.get_acquisition()
        return config_excerpt

    def _set_divisions(self, v_divs=8, h_divs=10):
        self._vertical_divisions = v_divs
        self._horizontal_divisions = h_divs

    def _alt_get_acquisition(self):
        """Alternative to convert acq to valid values

           Use this if ivi starts returning weird values for
           acquisition again
        """
        print_debug("getting acquisition")
        for key in self.acq_dict:
            value = getattr(self.instr.acquisition, key)
            if key == 'time_per_record':
                value = self._convert_special_acq(value)
            self.acq_dict[key] = value
        return self.acq_dict

    def _convert_special_acq(self, value):
        if value < 100000:
            return value
        elif value < 500000:
            value = 100000
        elif value < 5000000:
            value = 1000000
        elif value < 50000000:
            value = 10000000
        else:
            return value


class TransformerGRLTest(ScopeTransformer):

    def __init__(self, setup, instrument=None, session=None):
        """initializes transformer for grl tests

           setup - instructions from the server, should contain
           a 'config' which keys to a list of dicts with instructions
           for either the power controller (GRL-USB-PD) or the
           Tektronix scope (TektronixDPO7354C). This 'config' is
           assigned to the 'grl_config' attribute', a list used
           when the start_test is called
        """
        self.ce_dict = collections.defaultdict(lambda: {})
        self.ce_dict.update(DEFAULT_TEK_CONFIG)
        setup['config']['config_excerpt'] = json.dumps(self.ce_dict)
        ScopeTransformer.__init__(self, setup, instrument, session)
        self.exception_counter = 0
        self.logger = get_logger(log_filename='tek_grl_test.log',
                                 console_lvl=logging.INFO)
        self.config = collections.defaultdict(lambda: {})
        self.config.update(setup['config'])
        self.config['config_excerpt'] = self.ce_dict
        self.instr = instrument
        self.channels = self.instr.channels
        self.session = session
        self.time_step = 0.000001

        if instrument:
            self.tek = instrument
        else:
            try:
                self.logger.info("getting instrument")
                self.tek = get_instrument(self.test_run)
                self.tek.utility.reset()
            except Exception:
                self.exception_counter += 1
                self.logger.info("exception getting instrument", exc_info=True)
        try:
            self.logger.info("getting instrument")
            self.usbc = usb_controller.RawUsbController(vendor_id=0x227f,
                                                        product_id=0x0002)
        except Exception:
            self.exception_counter = 0
            self.logger.info("exception getting usb controller", exc_info=True)
        self.grl_config = self.grl_converter(setup['grl_config'])

    def grl_converter(self, config):
        for item in config:
            coms = item['commands']
            if not isinstance(coms, list):
                continue
            for i, c in enumerate(coms):
                coms[i] = c.decode('hex').strip()
        return config

    def set(self, obj, attr, val):
        """Sets the objects attribute (attr) with the value supplied and logs
        the success or error"""
        self.check_commands_completed()
        try:
            setattr(obj, attr, val)
            self.logger.info("TEK SUCCESS set %s with %s" % (attr, val))
        except Exception:
            self.logger.info("TEK ERROR: %s not set with %s" % (attr, val))
            self.logger.debug(traceback.format_exc())
            self.exception_counter += 1

    def write(self, command="", tek=None):
        """Writes to the tek with the _write function and logs the success or
        error. If no tek is supplied, the class tek object will be used."""
        self.check_commands_completed()
        if not tek:
            tek = self.tek
        try:
            tek._write(command)
            self.logger.info("TEK SUCCESS write:%s" % command)
        except Exception:
            self.logger.info("TEK ERROR: exception with write:%s" % command)
            self.logger.debug(traceback.format_exc())
            self.exception_counter += 1

    def start_test(self):
        configs = self.grl_config
        self.post_status_update("Commencing Transmitter Eye Diagram Test")
        self.logger.info("TS DEBUG: start_test ivi configs %s" % configs)
        for idx, config in enumerate(configs):
            if idx == 1:
                self.post_status_update("Configuring Scope")
            if idx == 6:
                self.post_status_update("Sending BIST Signal")
            if config['device'] == 'TektronixDPO7354C':
                self.config_tek(config)
            elif config['device'] == 'GRL-USB-PD':
                self.write_to_usbc(config['commands'])
            time.sleep(1)
        self.overlay()
        self.post_status_update("Completed Transmitter Eye Diagram Test")

    def config_tek(self, config):
        self.logger.info("TS DEBUG: config_tek ivi config %s" % config)
        if config['command_type'] == 'scpi':
            for command in config['commands']:
                self.write(command)
        elif config['command_type'] == 'python-ivi':
            self.pass_ivi_cmds(config['commands'])

    def write_to_usbc(self, commands):
        for command in commands:
            try:
                self.usbc.write(command=command)
            except Exception:
                self.logger.warning(traceback.format_exc())
                self.exception_counter += 1

    def get_voltage_list(self, volts):
        return [round_sig(float(volt)) for volt in volts]

    def pass_ivi_cmds(self, commands):
        self.logger.info("TS DEBUG: passing ivi commands %s" % commands)
        for command in commands:
            self.logger.info("TS DEBUG: ivi command: %s" % command)
            if command == 'fetch_waveform':
                self.post_status_update("Fetching Waveform")
                self.times['fetch_measurements_start'] = time.clock()
                self._set_enabled_list()
                self.time_step = 0.000001
                self.slice_dict = collections.defaultdict(int)
                self.first_slice = collections.defaultdict(int)
                start_tse = int(dt2ms(datetime.datetime.now()))
                self.trace_dict['Start_TSE'] = start_tse  # eventually remove
                self.trace_dict['start_tse'] = start_tse  # this is better
                print_debug("enabled_list: %s" % self.enabled_list)
                meas_dict = {}
                try:
                    ch = "ch1"
                    voltage_list = None
                    start_time = 0
                    end_time = 0
                    print_debug('invoking fetch_waveform')
                    waveform = self.tek.channels[
                        0].measurement.fetch_waveform()
                    print_debug("waveform length: %s" %
                                (len(waveform.x)), post=True)
                    times = waveform.t
                    start_time = times[0]
                    end_time = times[-1]
                    self.time_step = waveform.x_increment
                    voltage_list = self.get_voltage_list(waveform.y)
                    slice_list = self.get_slice_list(voltage_list)
                    self.slice_dict[ch] = slice_list
                    self.first_slice[ch] = slice_list[0]
                    mid = len(slice_list) / 2
                    self.mid_slices = slice_list[mid - 1:mid + 1]
                    meas_dict[ch] = collections.defaultdict(str)
                    self.trace_dict[ch + '_voltages'] = voltage_list
                    self.trace_dict[ch + '_start_time'] = start_time
                    self.trace_dict[ch + '_end_time'] = end_time
                    self.voltage_start_time = start_time  # default start_time
                    self.write_to_json_file(data=voltage_list,
                                            filename='grl-data.json')
                except Exception:
                    print("failed to fetch waveform for", ch)
                    print_debug(traceback.format_exc())
                self.trace_dict['raw_sec_btw_samples'] = self.time_step
                stop_tse = int(dt2ms(datetime.datetime.now()))
                self.trace_dict['Stop_TSE'] = stop_tse
                self.times['fetch_measurements_end'] = time.clock()
                return meas_dict
            elif command == 'fetch_setup':
                self.post_status_update("Fetching Setup")
                self.instrument_setup = self.tek.system.fetch_setup()

    def get_outputs(self, index=0):
        pass

    def overlay(self):
        overlay_volts = grl.get_volts_for_overlay(volts_file='grl-data.json')
        grl.count_and_post(overlay_volts, file_key='overlay-' + str(self.test_run_id))


def get_transformer(setup, instr, ses):
    test_run = setup['test_run']
    if test_run['instrument_type'] == 'TektronixMSO2024':
        i_transformer = TransformerMSO2024(setup, instr, ses)
    elif test_run['instrument_type'] == 'TektronixMDO3012':
        i_transformer = TransformerMDO3012(setup, instr, ses)
    elif test_run['g1_measurement'] == 'grl_test':
        i_transformer = TransformerGRLTest(setup, instr, ses)
    elif test_run['instrument_type'] == 'TektronixMSO5204B':
        i_transformer = TransformerMSO5204B(setup, instr, ses)
    elif test_run['instrument_type'] == 'GenericScope':
        i_transformer = ScopeTransformer(setup, instr, ses)
    else:
        i_transformer = Transformer(setup, instr, ses)
    return i_transformer
