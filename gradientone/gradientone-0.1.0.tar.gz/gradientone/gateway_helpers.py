#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import argparse
import ast
import datetime
import collections
import gzip
import os
import json
import requests
import signal
import subprocess
import traceback
import usb
import usbtmc
from math import log10
from requests_toolbelt.multipart.encoder import MultipartEncoder
import ivi

import re
import logging
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']


def print_debug(debug_statement, post=False, trace=False):
    if cfg.getboolean('client', 'DEBUG_ON'):
        print(debug_statement)
    if post:
        post_log(debug_statement)
    if trace:
        print(traceback.format_exc())
    if trace and post:
        post_log(traceback.format_exc())


def rotate_logfiles(original_file):
    for i in range(int(CLIENT_SETTINGS['MAX_NUM_LOGFILES'])):
        file_num = i + 1
        nextlogfile = original_file + "." + str(file_num)
        if not os.path.isfile(nextlogfile):
            break
        if os.stat(nextlogfile).st_size < int(CLIENT_SETTINGS['ELIGIBLE_LOGFILE_SIZE']):  # nopep8
            # purge the oldest file so that it's ready next rotate
            if file_num < int(CLIENT_SETTINGS['MAX_NUM_LOGFILES']):
                file_num += 1
                purge_logfile(original_file + "." + str(file_num))
            # break to return nextlogfile
            break
        # if all allowed files are full, purge and original
        if file_num == int(CLIENT_SETTINGS['MAX_NUM_LOGFILES']):
            purge_logfile(original_file)
            nextlogfile = original_file
    return nextlogfile


def purge_logfile(file):
    if not os.path.isfile(file):
        return
    try:
        os.remove(file)
    except Exception:
        print_debug("Remove logfile exception")


def get_logger(lvl=logging.INFO,
               log_filename=CLIENT_SETTINGS['DEFAULT_LOGFILE'],
               console_lvl=logging.WARNING,
               print_info=False,
               verbose=False,
               verbose_lvl=logging.DEBUG,
               verbose_file='verbose.log'):
    """Creates a logger that logs information to two files for different
    levels of logging. Note that if the verbose flag is true, the console
    level is simply overwritten to DEBUG level. This is added because
    'verbose=True' is easier to remember than console_lvl=logging.DEBUG"""

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # check if file exists
    if not os.path.isfile(log_filename):
        with open(log_filename, 'w') as f:
            f.write("init\n")
    # check logfile size and rotate if needed
    elif os.stat(log_filename).st_size > int(CLIENT_SETTINGS['ELIGIBLE_LOGFILE_SIZE']):  # nopep8
        log_filename = rotate_logfiles(log_filename)

    # create file handler
    console_handler = logging.StreamHandler()  # by default, sys.stderr
    file_handler = logging.FileHandler(log_filename)

    # set logging levels
    console_handler.setLevel(console_lvl)
    file_handler.setLevel(lvl)

    # create logging format
    formatter = logging.Formatter(
        '%(asctime)s :: [ %(levelname)s ] %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Note verbose flag will overwrite the console_lvl to the verbose_lvl
    if verbose:
        console_handler.setLevel(verbose_lvl)

    verbose_handler = logging.FileHandler(verbose_file)
    verbose_handler.setLevel(verbose_lvl)
    verbose_handler.setFormatter(formatter)
    logger.addHandler(verbose_handler)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


helper_logger = get_logger()


def get_headers(refresh=False, content_type='application/json'):
    headers = {'Content-type': content_type,
               'Gateway-Auth-Token': CLIENT_SETTINGS['GATEWAY_AUTH_TOKEN'],
               'Auth-Token': CLIENT_SETTINGS['GATEWAY_AUTH_TOKEN'],
               'Company-Name': COMMON_SETTINGS['COMPANYNAME']}
    return headers


def authorize_and_post(session, url, data):
    headers = get_headers()
    response = session.post(url, headers=headers, data=data)
    if response.status_code == 401:
        headers = get_headers(refresh=True)
        response = session.post(url, headers=headers, data=data)
    return response


def post_alert(session, message):
    """post a feedback update from instrument gateway"""
    health_url = ("https://" + COMMON_SETTINGS['DOMAIN'] +
                  "/testplansummary/" + COMMON_SETTINGS['COMPANYNAME'] +
                  '/' + COMMON_SETTINGS['HARDWARENAME'])
    payload = {
        'alert_message': message,
        'domain': COMMON_SETTINGS['DOMAIN'],
        'company': COMMON_SETTINGS['COMPANYNAME'],
        'gateway': COMMON_SETTINGS['HARDWARENAME'],
    }
    data = json.dumps(payload)
    authorize_and_post(session, health_url, data)


class SimulatedInstrument(ivi.tektronix.tektronixBaseScope.tektronixBaseScope):
    def __init__(self, *args, **kwargs):
        self.name = 'simulated'
        self._add_method('measurement.initiate',
                         self._measurement_initiate)
        self._add_method('measurement.fetch_waveform',
                         self._measurement_fetch_waveform)
        self._add_method('measurement.fetch_waveform_measurements',
                         self._measurement_fetch_waveform_measurements)
        self._add_property('identity.instrument_serial_number',
                           self._get_instrument_serial)
        self._add_property('identity.instrument_firmware_revision',
                           self._get_simulated_firmware_revision)
        self._add_method('channels[].measurement.fetch_waveform',
                         self._measurement_fetch_waveform)
        self._add_method('channels[].measurement.fetch_waveform_measurements',
                         self._measurement_fetch_waveform_measurements)
        self._add_property('channels[].probe_id',
                           self._get_channel_probe_id)
        self._add_property('channels[].enabled',
                           self._get_simulated_enabled)
        self._channel_count = 2
        self._analog_channel_count = 1
        self._digital_channel_count = 1
        self._init_channels()

    def close(self):
        pass

    def _get_channel_probe_id(self):
        return 'simulated_probe_id'

    def _get_simulated_firmware_revision(self):
        return 'simulated_firmware_version'

    def _get_instrument_serial(self):
        return 'simulated_serial_number'

    def _get_simulated_enabled(self, index=0):
        return True

    def _measurement_initiate(self):
        pass

    def _measurement_fetch_waveform(self, index):
        waveform = CLIENT_SETTINGS['SAMPLE_WAVEFORM']
        return waveform

    def _measurement_fetch_waveform_measurements(self, index):
        return None


def dt2ms(dtime):
    """Converts date time to miliseconds
    >>> from u2000_client import dt2ms
    >>> import datetime
    >>> dtime = datetime.datetime(2015, 12, 8, 18, 11, 44, 320012)
    >>> dt2ms(dtime)
    1449627104320
    """
    delta = dtime - datetime.datetime(1970, 1, 1)
    return int(delta.total_seconds()) * 1000 + int(delta.microseconds / 1000)


def log_wrap(execution, address):
    try:
        # return ivi.tektronix.tektronixMDO4104("TCPIP::192.168.1.108::INSTR")
        return execution(str(address))
    except Exception as e:
        helper_logger.critical(
            "instrument exception: " + str(e) + "|" + address + "|" + str(
                execution) + "|", exc_info=False)
        return None


def getAgilentU2000(addr=CLIENT_SETTINGS['AGILENT_U2000_ADDRESS']):
    return log_wrap(ivi.agilent.agilentU2001A, addr)


def getTektronixMDO4104(addr=CLIENT_SETTINGS['TEK_MDO4104_ADDRESS']):
    return log_wrap(ivi.tektronix.tektronixMDO4104, addr)


def getTektronixMDO3012(addr=CLIENT_SETTINGS['TEK_MDO3012_ADDRESS']):
    return log_wrap(ivi.tektronix.tektronixMDO3012, addr)

def getTektronixMSO2024(addr=CLIENT_SETTINGS['TEK_MSO2024_ADDRESS']):
    return log_wrap(ivi.tektronix.tektronixMSO2024, addr)

def getTektronixMSO5204B(addr=CLIENT_SETTINGS['TEK_MSO5204B_ADDRESS']):
    return log_wrap(ivi.tektronix.tektronixMSO5204B, addr)

# def getKeysightDSOS804A(addr=nuc_settings.KeysightDSOS804A_ADDR):
#     return log_wrap(ivi.agilent.agilentDSOS804A, addr)


def getGenericScope(addr=CLIENT_SETTINGS['GENERIC_SCOPE_ADDRESS']):
    return log_wrap(ivi.tektronix.tektronixMSO5204B,
                    addr)  # DPO7354C for the default scope


def get_instrument(test_run):
    helper_logger.info("Getting instrument")
    ivi_instruments = {
        'AgilentU2000': getAgilentU2000,
        'TektronixMDO4104': getTektronixMDO4104,
        'TektronixMDO3012': getTektronixMDO3012,
        'TektronixMSO2024': getTektronixMSO2024,
        'TektronixMSO5204B': getTektronixMSO5204B,
        'simulated': SimulatedInstrument,
        # 'KeysightDSOS804A': getKeysightDSOS804A,
        'GenericTektronix': getGenericScope,
    }

    ip_addr = None
    try:
        ip_addr = str(test_run['instrument_ip_address'])
    except Exception:
        helper_logger.debug("No valid instrument IP address", exc_info=True)

    device_id = manf_id = None
    try:
        device_id = str(test_run['usb_device_id'])
        manf_id = str(test_run['usb_manufacturer_id'])
    except Exception:
        helper_logger.debug("No valid instrument USB address", exc_info=True)

    instrument_type = None
    try:
        instrument_type = test_run['instrument_type']
    except Exception:
        helper_logger.debug("No valid instrument type", exc_info=True)

    addr = None
    if cfg.getboolean('client', 'SIMULATED'):
        instrument_type = 'simulated'
        helper_logger.debug("Using simulated instrument type", exc_info=True)
    elif ip_addr:
        addr = "TCPIP0::" + ip_addr + "::INSTR"
    elif device_id and manf_id:
        addr = "USB::" + manf_id + "::" + device_id + "::INSTR"
    else:
        helper_logger.debug("No address info, using defaults for instrument")
    helper_logger.info("calling ivi contructor with instrument type: %s"
                       % instrument_type)
    if addr:
        return ivi_instruments[instrument_type](addr)
    else:
        return ivi_instruments[instrument_type]()


def post_log(message, session=None):
    "posts logs to the server for info and troubleshooting"
    helper_logger.info("posting log message: %s" % message)
    if not session:
        session = requests.session()
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {
        'message': message,
        'time': datetime.datetime.now().isoformat(),
    }
    json_data = json.dumps(data, ensure_ascii=True)
    url_s = ("https://" + COMMON_SETTINGS['DOMAIN'] + "/nuc_logs/" +
             COMMON_SETTINGS['COMPANYNAME'] + '/' +
             COMMON_SETTINGS['HARDWARENAME'])
    response = session.post(url_s, data=json_data, headers=headers)
    helper_logger.info("post_log response: %s" % response)


def round_dec(val, decimal_place=3):
    """Rounds to a given decimal place and rounds up on 5
       >>> round_dec(0.0045)
       0.005
       >>> round_dec(4.5e-05)
       0.0
       >>> round_dec(4.5e-05, 5)
       5e-05
       """
    val += 0.01 * 10 ** -decimal_place
    rounded_val = round(val, decimal_place)
    if rounded_val > 1e+36:
        rounded_val = float(str(rounded_val))
    return rounded_val


def round_sig(val, digits=3):
    """Rounds value to specified significant digits by determining
       decimal place needed to round number value and calling round_dec
       >>> round_sig(6.3193e-9)
       6.32e-09
       >>> round_sig(6.3193e-9, 4)
       6.319e-09
       >>> round_sig(0.55550)
       0.556
       """
    if val == 0:
        return 0.0
    decimal_place = int(-log10(abs(val))) + digits
    return round_dec(val, decimal_place)


def safe_json_loads(eval_str, default=collections.defaultdict(int)):
    try:
        retval = json.loads(eval_str)
    except Exception:
        retval = legacy_ast(eval_str, default)
    return retval


def legacy_ast(eval_str, default=collections.defaultdict(int)):
    try:
        retval = ast.literal_eval(eval_str)
    except Exception:
        retval = default
    return retval


class Timer(object):
    def signal_handler(self, signum, frame):
        raise Exception("Timeouts: Timed out!")

    def set_timeout(self, seconds=10):
        signal.signal(signal.SIGALRM, self.signal_handler)
        signal.alarm(seconds)

    def clear_timeout(self):
        signal.alarm(0)


def reset_device_with_tag(search_string='Tektronix'):
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+)." +
                           "+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'),
                                                          dinfo.pop('device'))
                devices.append(dinfo)

    for d in devices:
        if search_string in d['tag']:
            device_path = d['device']
        else:
            device_path = '/dev/bus/usb/002/003'

    print_debug("resetting %s" % device_path, post=True)
    e = '../../HelperScripts/usbreset ' + device_path
    subprocess.call(e, shell=True)


def post_logfile(test_run_id=""):
    default_logfile = CLIENT_SETTINGS['DEFAULT_LOGFILE']
    zlogfile = default_logfile + '.gz'
    with open(default_logfile) as f_in, gzip.open(zlogfile, 'wb') as f_out:
        f_out.writelines(f_in)
    data_type = 'application/x-gzip'
    multipartblob = MultipartEncoder(
        fields={
            'file': (zlogfile, open(zlogfile, 'rb'), data_type),
            'test_run_id': str(test_run_id),
            'company_nickname': COMMON_SETTINGS['COMPANYNAME'],
        }
    )
    blob_url = requests.get(
        "https://" + COMMON_SETTINGS['DOMAIN'] + "/upload/logfile/geturl")
    hdrs = {'Content-Type': multipartblob.content_type}
    response = requests.post(blob_url.text,
                             data=multipartblob,
                             headers=hdrs,
                             )
    print_debug("post_logfile response.reason: %s" % response.reason)
    print_debug("post_logfile response.status_code: %s" % response.status_code)


def authorize_and_request(url):
    headers = get_headers()
    ses = requests.session()
    response = ses.get(url, headers=headers)
    return response, ses


def decimation_factor(record_length):
    """Returns decimation factor based on record length"""
    dec_factors = {100000: 10, 125000: 12, 1000000: 100,
                   1250000: 125, 5000000: 500, 10000000: 1000, 20000000: 2000}
    factor = dec_factors[record_length]
    return factor


def get_usb_devices():
    """Returns list of all usb devices, including peripherals"""
    device_re = re.compile(
        "Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)  # noqa
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = ('/dev/bus/usb/%s/%s'
                                   % (dinfo.pop('bus'), dinfo.pop('device')))
                devices.append(dinfo)
    return devices


def get_usbtmc_devices():
    """Returns list of usbtmc devices with manf, prod, and serial"""
    device_list = usbtmc.list_devices()
    instruments = []
    for dev in device_list:
        if dev is None:
            helper_logger.warning('Device is not connected')
        else:
            dev._langids = (1033,)
            if dev._manufacturer is None:
                try:
                    dev._manufacturer = usb.util.get_string(dev, dev.iManufacturer)
                except Exception as e_msg:
                    print("failed to get manufacturer with dev: ", dev)

            man = str(dev._manufacturer)
            # manufacturers.append(man)
            if dev._product is None:
                dev._product = usb.util.get_string(dev, dev.iProduct)
            prod = str(dev._product)
            # products.append(prod)
            serial = usb.util.get_string(dev, dev.iSerialNumber)
            inst_dict = {
                'manufacturer': man,
                'product': prod,
                'serial': serial,
            }
            instruments.append(inst_dict)
    return instruments


def authorize_and_get(url):
    """Authorizes request to url and makes GET"""
    headers = get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        headers = get_headers(refresh=True)
        response = requests.get(url, headers=headers)
    return response


def check_args():
    """Checks command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("a", nargs='?', default="check_string_for_empty")
    args = parser.parse_args()
    if args.a == 'check_string_for_empty':
        print('No argument was given')
    elif args.a == 'magic.name':
        print('You nailed it!')
    else:
        print(args.a)

