#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""


import collections
import csv
import json
import requests
import numpy as np
import gzip
import traceback
import zlib
from configparser import ConfigParser
from requests_toolbelt.multipart.encoder import MultipartEncoder

import gateway_helpers
from gateway_helpers import print_debug

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

logger = gateway_helpers.get_logger(
    log_filename=CLIENT_SETTINGS['DEFAULT_LOGFILE'])


class Transmitter(object):
    # Transmits trace data received from instrument up to the server

    def __init__(self, session):
        self.session = session


class CANOpenTransmitter(Transmitter):
    """
    Transmits data for CANOpen devices
    """

    def __init__(self, session):
        Transmitter.__init__(self, session=session)


class ScopeTransmitter(Transmitter):
    """transmits data to server for scope information"""

    def __init__(self, transformer=None, trace_data=None, session=None):
        Transmitter.__init__(self, session=session)
        self.test_run = collections.defaultdict(int)
        if transformer:
            self.test_run.update(transformer.test_run)
            self.test_run_id = self.test_run['id']
            self.time_step = transformer.time_step
            # the transformer ce_dict holds initial instructions
            self.ce_dict = transformer.ce_dict
            self.config_scorecard = transformer.config_scorecard
            self.g1_measurement_results = transformer.g1_measurement_results
        else:
            self.ce_dict = {}
            self.time_step = 1.0
        self.trace_dict = collections.defaultdict(int)
        if trace_data:
            self.trace_dict.update(trace_data)

        self.blob_key = None
        self.b_idx = 0
        self.raw_data_url = (
            "https://" + COMMON_SETTINGS['DOMAIN'] + "/tektronixdata/" +
            str(self.trace_dict['test_run_id'])
        )

        # this is updated with the reported config_excerpt
        if "config_excerpt" in self.trace_dict.keys():
            self.ce_dict.update(self.trace_dict['config_excerpt'])
        self.ch_start_times = collections.defaultdict(int)
        self.ch_end_times = collections.defaultdict(int)
        self.config_scorecard = transformer.config_scorecard
        self.more_metadata = collections.defaultdict(str)

        if cfg.getboolean('client', 'SIMULATED'):
            self.ce_dict['enabled_list'] = ['ch1']
        if "enabled_list" in self.ce_dict.keys():
            for ch in self.ce_dict['enabled_list']:
                start_key = ch + '_start_time'
                end_key = ch + '_end_time'
                self.ch_start_times[start_key] = self.trace_dict[start_key]
                self.ch_end_times[end_key] = self.trace_dict[end_key]
            # last start/stop time for default
            if start_key in self.trace_dict.keys():
                self.voltage_start_time = self.trace_dict[start_key]
        self.results_dict = {
            'test_run_id': self.trace_dict['test_run_id'],
            'channel_headers': self.ce_dict['enabled_list'],
            'test_results': transformer.first_slice,
            'hardware_name': COMMON_SETTINGS['HARDWARENAME'],
            'company_nickname': COMMON_SETTINGS['COMPANYNAME'],
            'i_settings': self.trace_dict['i_settings'],
            'raw_data_url': self.raw_data_url,
            'start_tse': int(self.trace_dict['start_tse']),
            'test_plan': self.trace_dict['test_plan'],
            'config_name': self.trace_dict['config_name'],
            'test_run_name': self.trace_dict['test_run_name'],
            'instrument_type': self.trace_dict['instrument_type'],
            'record_length': self.trace_dict['record_length'],
            'time_per_record': self.ce_dict['acquisition']['time_per_record'],
            'time_step': self.time_step,
            # 'measurements': self.trace_dict['meas_dict'],
            # 'instrument_information': self.trace_dict['instr_info'],
            'voltage_start_time': self.voltage_start_time,
            'ch_start_times': self.ch_start_times,
            'ch_end_times': self.ch_end_times,
        }
        self.dec_factor = None
        self.slices = []

    def post_full_length_waveform(self):
        """Sends max dataset for full waveform views"""
        test_run_id = self.trace_dict['test_run_id']
        url_d = "https://" + \
            COMMON_SETTINGS['DOMAIN'] + "/tek_decimated/" + str(test_run_id)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        v_dict = {}

        for ch in self.ce_dict['enabled_list']:
            voltage_list = self.trace_dict[ch + '_voltages']
            if not voltage_list:
                voltage_list = []
            if len(voltage_list) > int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER']):  # nopep8
                v_dict[ch] = self.shrink(voltage_list)
            else:
                v_dict[ch] = voltage_list
        self.full_length_voltage_data = v_dict

        payload = {
            'time_step': self.time_step,
            'dec_factor': self.dec_factor,
            'test_results': self.full_length_voltage_data,
            'voltage_start_time': self.voltage_start_time,
        }
        json_data = json.dumps(payload, ensure_ascii=True)
        print_debug("posting end to end waveform")
        response = self.session.post(url_d, data=json_data, headers=headers)
        print_debug(response)

    def shrink(self, voltage_list, mode='normal', max_length=CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER']):
        print_debug("shrinking voltage_list")
        len_voltage_list = len(voltage_list)
        self.dec_factor = len_voltage_list / int(max_length)
        self.dec_time_step = self.dec_factor * self.time_step
        shrunk_list = [voltage_list[0]]
        index = int(self.dec_factor)

        while index < len_voltage_list:
            if mode == 'normal':
                shrunk_list.append(voltage_list[index])
                index += int(self.dec_factor)
            elif mode == 'average':
                index += int(self.dec_factor)
                mean_value = np.mean(
                    voltage_list[index - int(self.dec_factor): index])
                shrunk_list.append(mean_value)
            elif mode == 'downsample':
                # use scipy.signal.downsample
                pass
            elif mode == 'voltage_peak_to_peak':
                self.dec_factor = self.dec_factor * 2
        return shrunk_list

    def transmit_blob(self):
        """Sends test results to the blobstore.

        End to end waveforms are sent here.
        """
        print_debug("transmitting blob")
        config_name = self.trace_dict['config_name']
        filename = config_name + ':' + str(self.trace_dict['test_run_id'])
        fileblob = open('tempfile.csv', 'w')
        cwriter = csv.writer(fileblob)
        cwriter.writerow(self.ce_dict['enabled_list'])
        voltage_lists = []
        for ch in self.full_length_voltage_data:
            voltage_lists.append(self.full_length_voltage_data[ch])
        for row in zip(*voltage_lists):
            cwriter.writerow(row)
        fileblob.close()
        with open('tempfile.csv') as f_in, gzip.open('tempfile.gz', 'wb') as f_out:  # nopep8
            f_out.writelines(f_in)
        data_file_name = 'tempfile.gz'
        data_type = 'application/x-gzip'
        multipartblob = MultipartEncoder(
            fields={
                'file': (filename, open(data_file_name, 'rb'), data_type),
                'test_run_id': str(self.trace_dict['test_run_id']),
                'dec_factor': str(self.dec_factor)
            }
        )
        blob_url = requests.get("https://" + COMMON_SETTINGS['DOMAIN'] +
                                "/upload_tek/geturl")
        response = requests.post(blob_url.text, data=multipartblob,
                                 headers={
                                    'Content-Type': multipartblob.content_type
                                    })
        print_debug("transmitblob response.reason: %s" % response.reason)
        print_debug("transmitblob response.status_code: %s"
                    % response.status_code)
        self.blob_key = response.text

    def transmit_file(self, filename, content_type='application/x-gzip'):
        """transmits file to blobstore

        assumes the file is already gzipped
        """
        test_run_id = str(self.trace_dict['test_run_id'])
        if not filename:
            filename = test_run_id + "-" + self.b_idx + ".gz"
        multipartblob = MultipartEncoder(
            fields = {
                'file':(filename, open(filename, 'rb'), content_type),
                'test_run_id':test_run_id,
                'blob_index': str(self.b_idx),
                'file_key': test_run_id + '-' + filename,
            }
        )
        resp = requests.get("https://" + COMMON_SETTINGS['DOMAIN']
                                + "/upload/geturl")
        headers = {'Content-Type': multipartblob.content_type}
        response = requests.post(url=resp.text, data=multipartblob, headers=headers)
        self.blob_key = response.text
        self.b_idx += 1

    def transmit_slice_blobs(self):
        for idx, slice_data in enumerate(self.slices):
            filename='slice-' + str(idx) + '.json.gz'
            with gzip.open(filename, 'wb') as f:
                f.write(json.dumps(slice_data))
            self.transmit_file(filename=filename)

    def transmit_slices(self):
        # post slices
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        slice_url = "https://" + COMMON_SETTINGS['DOMAIN'] + "/tek_slice"
        voltage_start_time = self.voltage_start_time
        dict_of_slice_lists = collections.defaultdict(int)
        for ch in self.ce_dict['enabled_list']:
            voltages = self.trace_dict[ch + '_voltages']
            # create list of slices
            list_of_slices = [voltages[x:x+int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER'])]  # nopep8
                for x in range(0, len(voltages), int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER']))]  # nopep8
            dict_of_slice_lists[ch] = list_of_slices
            print_debug("length of list of slices for %s: %s"
                        % (ch, len(list_of_slices)))
            self.more_metadata['total_points'] = len(voltages)
        for idx, slice_points in enumerate(list_of_slices):
            slices_by_channel = {}
            for ch in dict_of_slice_lists:
                if idx + 1 > len(dict_of_slice_lists[ch]):
                    print_debug("""Warning! Slice index greater than length of
                        list of slices for %s""" % ch, post=True)
                else:
                    slices_by_channel[ch] = dict_of_slice_lists[ch][idx]
            voltage_start_time += self.time_step * len(slice_points)
            slice_data = {
                'test_run_id': self.trace_dict['test_run_id'],
                'slice_index': idx,
                'num_of_slices': len(list_of_slices),
                'voltage_start_time': voltage_start_time,
                'time_step': self.time_step,
                'test_results': slices_by_channel,
            }
            self.slices.append(slice_data)
            slice_data = json.dumps(slice_data, ensure_ascii=True)
            headers['content-encoding'] = 'gzip'
            slice_data = zlib.compress(json.dumps(slice_data))
            self.session.post(slice_url, data=slice_data, headers=headers)
        self.more_metadata['num_of_slices'] = len(list_of_slices)
        self.more_metadata['slice_length'] = int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER'])  # nopep8


    def test_complete(self):
        """transmit test complete function sends a json object that is used
           to update DB on test status. Primarily metadata and indexing.
           No waveforms are sent here.
        """
        print_debug("testcomplete transmission")
        test_run_id = self.trace_dict['test_run_id']
        chart_url = 'https://' + \
            COMMON_SETTINGS['DOMAIN'] + '/result/' + str(test_run_id)
        screenshot_url = ('https://' + COMMON_SETTINGS['DOMAIN'] +
                          '/view_report_file/' +
                          str(self.trace_dict['screenshot_blob_key']))
        self.trace_dict['instr_info']['scope_screenshot_url'] = screenshot_url
        extra_data = {
            'stop_tse': self.trace_dict['Stop_TSE'],
            'blob_key': self.blob_key,
            'results_link': chart_url,
            'test_results': self.raw_data_url,
            'config_information': self.trace_dict['config_info'],
            'config_excerpt': self.trace_dict['config_excerpt'],
            'measurements': self.trace_dict['meas_dict'],
            'instrument_information': self.trace_dict['instr_info'],
            'more_options': self.trace_dict['more_options'],
            'g1_measurement': self.trace_dict['g1_measurement'],
            'dec_factor': self.dec_factor,
            'config_scorecard': self.config_scorecard,
            'more_metadata': self.more_metadata,
            'g1_measurement_results': self.g1_measurement_results,
            'company_nickname': COMMON_SETTINGS['COMPANYNAME'],
            'instrument_type': self.trace_dict['instrument_type'],
        }

        self.results_dict.update(extra_data)
        data = json.dumps(self.results_dict)
        url = "https://" + COMMON_SETTINGS['DOMAIN'] + "/testcomplete"
        self.post_data(url=url, data=data)
        url = ("https://" + COMMON_SETTINGS['DOMAIN'] +
               "/polling/results/metadata/" + str(self.test_run_id))
        self.post_data(url=url, data=data)

    def post_data(self, url, data="", headers=""):
        if not headers:
            headers = gateway_helpers.get_headers()
        response = self.session.post(url, data=data, headers=headers)
        print_debug(url + " response.reason= %s" % response.reason)
        print_debug(url + " response.status_code=%s" % response.status_code)
        return response

    def transmit_config(self):
        """Posts config to server for storage"""
        payload = {
            'config_excerpt': self.trace_dict['config_excerpt'],
            'config_data': {
                'new_config_name': self.trace_dict['test_run_id'],
                'hybrid_config': self.trace_dict['config_info'],
                'instrument_type': self.trace_dict['instrument_type'],
                'company_nickname': COMMON_SETTINGS['COMPANYNAME'],
            }
        }
        url = "https://" + COMMON_SETTINGS['DOMAIN'] + "/create_config"
        self.post_data(url=url, data=json.dumps(payload))

    def transmit_logs(self, to_blob=False):
        filename = str(self.test_run_id) + '.log'
        if to_blob:
            # TODO: add functionality
            # transmit_logs(test_run_id=self.test_run_id)
            return
        # else it will just go to memcache
        multipartblob = MultipartEncoder(
            fields={
                'logfile': (filename, open('client.log', 'rb'), 'text/plain'),
                'testrunid': str(self.test_run_id),
            }
        )
        log_url = "https://" + \
            COMMON_SETTINGS['DOMAIN'] + "/logs/" + str(self.test_run_id)
        headers={'Content-Type': multipartblob.content_type},
        resp = self.post_data(url=log_url, data=multipartblob, headers=headers)
        print_debug(resp.text)


class GRLTransmitter(ScopeTransmitter):
    """transmits data to server for GRL tests"""

    def __init__(self, transformer, trace_data, session):
        ScopeTransmitter.__init__(transformer, trace_data, session)

    def transmit_slices(self):
        # post slices
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        slice_url = "https://" + COMMON_SETTINGS['DOMAIN'] + "/tek_slice"
        voltage_start_time = self.voltage_start_time
        dict_of_slice_lists = collections.defaultdict(int)
        list_of_slices = []
        ch = 'ch1'
        voltages = self.trace_dict[ch + '_voltages']
        # create list of slices
        list_of_slices = [voltages[x:x + int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER'])]  # nopep8
                          for x in range(0, len(voltages), int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER']))]  # nopep8
        dict_of_slice_lists[ch] = list_of_slices
        print_debug("length of list of slices for %s: %s" %
                    (ch, len(list_of_slices)))
        for slice_index, slice_points in enumerate(list_of_slices):
            slices_by_channel = {}
            for ch in dict_of_slice_lists:
                if slice_index + 1 > len(dict_of_slice_lists[ch]):
                    print_debug("""Warning! Slice index greater than length of
                        list of slices for %s""" % ch, post=True)
                else:
                    slices_by_channel[ch] = dict_of_slice_lists[
                        ch][slice_index]
            voltage_start_time += self.time_step * len(slice_points)
            slice_data = {
                'test_run_id': self.trace_dict['test_run_id'],
                'slice_index': slice_index,
                'num_of_slices': len(list_of_slices),
                'voltage_start_time': voltage_start_time,
                'time_step': self.time_step,
                'test_results': slices_by_channel,
            }
            slice_data = json.dumps(slice_data, ensure_ascii=True)
            if cfg.getboolean('client', 'USE_GZIP'):
                headers['content-encoding'] = 'gzip'
                slice_data = zlib.compress(json.dumps(slice_data))
            self.session.post(slice_url, data=slice_data, headers=headers)

    def post_full_length_waveform(self):
        """Sends max dataset for full waveform views"""
        test_run_id = self.trace_dict['test_run_id']
        url_d = "https://" + \
            COMMON_SETTINGS['DOMAIN'] + "/tek_decimated/" + str(test_run_id)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        v_dict = {}
        ch = 'ch1'
        voltage_list = self.trace_dict[ch + '_voltages']
        if len(voltage_list) > int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER']):  # nopep8
            v_dict[ch] = self.shrink(voltage_list)
        else:
            v_dict[ch] = voltage_list
        self.full_length_voltage_data = v_dict

        payload = {
            'time_step': self.time_step,
            'dec_factor': self.dec_factor,
            'test_results': self.full_length_voltage_data,
            'voltage_start_time': self.voltage_start_time,
        }
        json_data = json.dumps(payload, ensure_ascii=True)
        print_debug("posting to %s" % url_d)
        response = self.session.post(url_d, data=json_data, headers=headers)
        print_debug(response)

    def transmit_blob(self, infile='grl-data.json'):
        """Sends test results to the blobstore

        End to end waveforms are sent here.
        """
        print_debug("transmitting blob")
        gzip_file = infile + '.gz'
        config_name = self.trace_dict['config_name']
        with open(infile) as f_in, gzip.open(gzip_file, 'wb') as f_out:
            f_out.writelines(f_in)
        data_type = 'application/x-gzip'

        blobfile = str(config_name) + ':' + str(self.trace_dict['test_run_id'])
        multipartblob = MultipartEncoder(
            fields={
                'file': (blobfile, open(gzip_file, 'rb'), data_type),
                'test_run_id': str(self.trace_dict['test_run_id']),
                'dec_factor': str(self.dec_factor)
            }
        )
        blob_url = requests.get("https://" + COMMON_SETTINGS['DOMAIN'] +
                                "/upload/geturl")
        response = requests.post(blob_url.text,
                                 data=multipartblob,
                                 headers={
                                    'Content-Type': multipartblob.content_type
                                    })
        print_debug("transmitblob response.reason: %s" % response.reason)
        print_debug("transmitblob response.status_code: %s" %
                    response.status_code)
        self.blob_key = response.text


def get_transmitter(i_transformer=None, trace_data=None, session=None):
    if not session:
        session = requests.session()
    if not trace_data:
        return CANOpenTransmitter(session)
    try:
        if trace_data['test_run']['g1_measurement'] == 'grl_test':
            return GRLTransmitter(i_transformer, trace_data, session)
        else:
            return ScopeTransmitter(i_transformer, trace_data, session)
    except TypeError:
        return ScopeTransmitter(i_transformer, trace_data, session)
    except KeyError:
        return ScopeTransmitter(i_transformer, trace_data, session)
    except Exception:
        print_debug("Unexpected exception in getting transmitter")
        return None


def transmit_basic(trace, ses):
    """results transmission for basic instruments, such as powermeters"""
    if not trace:
        print_debug("No Trace. Run Failed", post=True)
        return
    try:
        trace.transmitraw()
        trace.transmitblob()
        trace.testcomplete()
    except Exception:
        logger.error("Exception occurred during trace transmission")
        logger.error(traceback.format_exc())
    finally:
        tid = trace.trace_dict['test_run_id']
        gateway_helpers.post_logfile(test_run_id=tid)


def transmit_advanced(trace, ses):
    """results transmission for advanced instruments, tektronix"""
    try:
        print_debug("transmitting trace", post=True)
        trace.post_full_length_waveform()
        trace.transmit_slices()
        trace.transmit_slice_blobs()
        trace.transmit_blob()  # slower transmission to blobstore
        trace.test_complete()  # complete transmission indexing blobstore data
    except Exception:
        logger.error("Exception occurred during trace transmission")
        logger.error(traceback.format_exc())
    finally:
        tid = trace.trace_dict['test_run_id']
        gateway_helpers.post_logfile(test_run_id=tid)


def transmit_trace(trace, test_run, ses):
    if not trace:
        print_debug(
            "ERROR: No trace from instrument to transmit", post=True)
        return
    basic_list = ['AgilentU2000']
    advanced_list = COMMON_SETTINGS['ADVANCED_INSTRUMENT_TYPES']
    if test_run['instrument_type'] in basic_list:
        transmit_basic(trace, ses)
    elif test_run['instrument_type'] in advanced_list:
        transmit_advanced(trace, ses)
    else:
        logger.warning("no matching transmission method for %s" %
                       test_run['instrument_type'])
