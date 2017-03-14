#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import collections
import multiprocessing as multi
import time
import traceback
from configparser import ConfigParser
import usb

import gateway_helpers
import tek_grl_configs
import transformers
import transmitters
from gateway_helpers import print_debug


cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']

### REMOVE THIS BEFORE IT GOES TO THE CLIENT
try:
    from raven import Client
    SENTRY_CLIENT = Client(cfg['client']['SENTRY'])
except Exception:
    SENTRY_CLIENT = gateway_helpers.MySentry()
###


CLIENT_ID = 'ORIGINAL'
SAMPLE_FILE = 'MDO30121M.txt'
CONFIG_URL = ('https://' + COMMON_SETTINGS['DOMAIN'] + '/testplansummary/' +
              COMMON_SETTINGS['COMPANYNAME'] + '/' +
              COMMON_SETTINGS['HARDWARENAME'])
DEFAULT_TEK_TYPE = 'TektronixMDO3012'


logger = gateway_helpers.get_logger(
    log_filename=CLIENT_SETTINGS['DEFAULT_LOGFILE'])


class TestRunner(object):
    """TestRunner runs the 'test' instructions form the server

       Note that a 'test' is not always an actual pass/fail test,
       the 'test' could be a configured scope waveform trace, or
       just a powermeter reading, or instructions for a motor, etc.

       run_the_setup - this is the top level function that gets
                       when the client code creates a test_run
       single_run - most test runs will call this for a single run
       get_trace - when a trace is needed from the instrument,
                   this uses a Transformer for the instrument
                   to pass instructions and get the trace data,
                   then returns a Transmitter to send to server
    """

    def __init__(self, setup, session):
        super(TestRunner, self).__init__()
        self.setup = setup
        self.session = session
        self.test_run = collections.defaultdict(str)
        self.test_run.update(self.setup['test_run'])
        self.inst_dict = collections.defaultdict(str)
        self.inst_dict['pass_fail'] = 'N/A'
        self.inst_dict['test_plan'] = self.test_run['test_plan']
        # Timer sets and clears the timeouts
        self.timer = gateway_helpers.Timer()

    def run_the_setup(self):
        ses = self.session
        test_run = self.test_run
        trace = None
        if test_run['test_type'] == 'GRL':
            self.run_grl_test()
        elif test_run['test_type'] == 'MotorController':
            # TODO: include motor case
            # run motor commands
            # create the transformer to send commands
            # use transmitter to send response to server
            pass
        elif test_run['single_run']:
            trace = self.single_run()
        elif test_run['start_repeating']:
            pass
        elif test_run['stop_repeating']:
            pass
        elif test_run['hybrid'] or test_run['autoset']:
            print_debug("cloud capture or autoset order received")
            trace = self.get_trace(self.setup, ses)
        elif test_run['reset_usb_device']:
            tag = test_run['device_tag']
            if not tag:
                tag = 'Tektronix'
            gateway_helpers.reset_device_with_tag(tag)
        else:
            logger.warning("test_run with no control commands")
        if trace:
            transmit_ps = multi.Process(target=transmitters.transmit_trace,
                                        args=(trace, test_run, ses),
                                        name='nanny_process:' +
                                        COMMON_SETTINGS['DOMAIN'])
            transmit_ps.start()

    def run_grl_test(self):
        grl = tek_grl_configs.Grl_Test()
        result = grl.run_grl_test()
        print_debug("grl result:" % result)

    def single_run(self):
        print_debug("Received single run start order", post=True)
        ses = self.session
        trace = None
        try:
            trace = self.get_trace(self.setup, ses)
        except usb.core.USBError as e:
            print_debug("USBError!", post=True, trace=True)
            gateway_helpers.handle_usb_error(ses, e)
        except Exception:
            logger.error("unexpected exception in running trace")
            logger.error(traceback.format_exc())
            SENTRY_CLIENT.captureException("unexpected exception in running trace")
        return trace

    def _get_instrument(self):
        self.timer.set_timeout(30)
        instr = None
        try:
            print_debug("getting instrument")
            instr = gateway_helpers.get_instrument(self.test_run)
        except usb.core.USBError:
            print_debug("USBError!", post=True, trace=True)
            # reset and retry
            gateway_helpers.reset_device_with_tag()
            time.sleep(1)
            instr = gateway_helpers.get_instrument(self.test_run)
        except Exception:
            print_debug("failed to get instrument instance...")
            print_debug(traceback.format_exc())
            SENTRY_CLIENT.captureException("failed to get instrument instance...")
        if not instr:
            print_debug("no instrument for trace...")
            return None
        self.timer.clear_timeout()
        return instr

    def _get_transformer(self, instr=None):
        try:
            i_transformer = transformers.get_transformer(self.setup, instr,
                                                         self.session)
        except Exception:
            print_debug("unable to build transformer... no trace")
            print_debug("closing intrument without receiving trace")
            instr.close()
            print_debug(traceback.format_exc())
            SENTRY_CLIENT.captureException("unable to build transformer... no "
                                      "trace")
            return None
        return i_transformer

    def get_trace(self, setup, ses, final_attempt=False):
        """ Gets a trace from the instrument.

            This uses a Transformer for the instrument to pass
            instructions and get the trace data, then returns a
            trace object. The trace object is an instance of
            Transmitter that transmits the trace results and test
            run related data. By default it will retry once in case
            it fails on the first try.
        """
        print_debug("get trace called")
        # obtain instrument for trace
        instr = self._get_instrument()
        # get transformer for instrument
        i_transformer = self._get_transformer(instr)

        # get trace from instrument by running setup with transformer
        trace = None
        try:
            print_debug("running trace setup")
            trace = self.process_transformer(i_transformer)
            print_debug("process_transformer ran with no errors")
        except KeyError:
            print_debug("KeyError exception in running setup",
                        post=True, trace=True)
            print_debug(traceback.format_exc())
            SENTRY_CLIENT.captureException("KeyError exception in running setup")
            # no retry on key errors
        except Exception:
            print_debug("Run config failed. Unexpected error",
                        post=True, trace=True)
            SENTRY_CLIENT.captureException("Run config failed. Unexpected error")
            # unexpected error, try again
            trace = self.process_transformer(i_transformer)
        finally:
            print_debug("instrument processing complete, closing connection")
            i_transformer.instr.close()
            return trace

    def get_initial_excerpt(self, i_transformer):
        """Returns the intial config excerpt from instrument

        It's important to call this before fetching measurements.
          1) It initializes the instrument and syncs up transformer
          2) It gets an initial state, which is good for debugging

        i_transformer: object that reads back the appropriate
                       fields for the instrument type

        """
        self.timer.set_timeout(240)
        try:
            initial_excerpt = i_transformer.get_config_excerpt()
            msg = "initial config setup from instrument: %s" % initial_excerpt
            print_debug(msg, post=True)
        except usb.core.USBError as e:
            print_debug("USBError!", post=True, trace=True)
            i_transformer.handle_usb_error(e)
        except Exception:
            print_debug("exception in config_excerpt initialization",
                        post=True, trace=True)
            SENTRY_CLIENT.captureException("exception in config_excerpt initialization")
        self.timer.clear_timeout()
        return initial_excerpt

    def load_config(self, i_transformer, trace_dict):
        """loads config to instrument"""
        test_run = self.test_run
        if test_run['hybrid'] or test_run['autoset']:
            print_debug("measuring without loading config")
            self.inst_dict['config_name'] = str(test_run['id'])
            trace_dict['config_name'] = str(test_run['id'])
        else:
            self.inst_dict['config_name'] = self.config['name']
            trace_dict['config_name'] = self.config['name']
            self.timer.set_timeout(60)
            try:
                i_transformer.load_config()
            except usb.core.USBError as e:
                print_debug("USBError!", post=True, trace=True)
                i_transformer.handle_usb_error(e)
            except Exception:
                print_debug("Exception in calling load_config()", post=True)
                print_debug(traceback.format_exc(), post=True)
                SENTRY_CLIENT.captureException("Exception in calling load_config()")
            self.timer.clear_timeout()

    def get_meas_dict(self, i_transformer):
        print_debug("initiate measurement")
        i_transformer.instr.measurement.initiate()
        self.timer.set_timeout(300)
        meas_dict = collections.defaultdict(str)
        try:
            meas_dict = i_transformer.fetch_measurements()
        except usb.core.USBError as e:
            print_debug("USBError Fetching measurments", post=True, trace=True)
            i_transformer.handle_usb_error(e)
        except Exception:
            print_debug("fetch_measurements exception")
            print_debug(traceback.format_exc())
            SENTRY_CLIENT.captureException()
        self.timer.clear_timeout()
        return meas_dict

    def get_instrument_info(self, i_transformer):
        self.timer.set_timeout(120)
        instr_info = collections.defaultdict(str)
        try:
            instr_info = i_transformer.get_instrument_info()
        except Exception:
            print_debug("fetch instrument info exception",
                        post=True, trace=True)
            SENTRY_CLIENT.captureException("fetch instrument info exception")
        self.timer.clear_timeout()
        return instr_info

    def get_metadata(self, i_transformer):
        metadata = collections.defaultdict(str)
        metadata.update(i_transformer.trace_dict)
        metadata['instr_info'] = self.get_instrument_info(i_transformer)
        self.timer.set_timeout(120)
        try:
            # instrument fetch_setup dump
            metadata['config_info'] = i_transformer.fetch_config_info()
            # read instrument using ivi fields
            metadata['config_excerpt'] = i_transformer.get_config_excerpt()
        except Exception:
            print_debug("post-trace fetch config exception",
                        post=True, trace=True)
            metadata['config_info'] = collections.defaultdict(str)
            metadata['config_excerpt'] = collections.defaultdict(str)
            SENTRY_CLIENT.captureException("post-trace fetch config exception")
        self.timer.clear_timeout()
        i_transformer.times['complete'] = time.clock()
        i_transformer.update_scorecard_times()
        return metadata

    def update_with_test_run_info(self, trace_dict, test_run):
        trace_dict['test_run_name'] = test_run['name']
        trace_dict['test_plan'] = test_run['test_plan']
        trace_dict['test_run_id'] = test_run['id']
        trace_dict['instrument_type'] = test_run['instrument_type']
        trace_dict['g1_measurement'] = test_run['g1_measurement']
        return trace_dict

    def process_transformer(self, i_transformer):
        """Runs the setup on the instrument to get trace with measurments

        Called by get_trace(), this function processes transformer to
        collect instrument data, including measurements, config, and
        other metadata. These make up a trace_dict that is passed to
        the Transmitter constructor.

            i_transformer: Transfomer object being processed. This is used
                           to build a trace_dict to then use for the
                           Transmitter contructor.

        Returns a Transmitter object to transmit the trace
        """
        test_run = self.test_run
        test_run.update(i_transformer.test_run)
        trace_dict = collections.defaultdict(str)
        ses = i_transformer.session
        # reset config if 'hybrid' flag found
        if test_run['hybrid']:
            self.config = 'hybrid'
        else:
            self.config = i_transformer.config
        print_debug("config in setup is: %s" % self.config)
        # sets the ivi usb timeout
        i_transformer.instr._interface.timeout = 25000
        # check for special grl_test
        if test_run['g1_measurement'] == 'grl_test':
            print("name = ", test_run['config_name'])
            self.inst_dict['config_name'] = str(test_run['config_name'])
            trace_dict['config_name'] = self.config['name']
            i_transformer.start_test()
            trace_dict['meas_dict'] = collections.defaultdict(str)
        else:
            trace_dict['initial_excerpt'] = self.get_initial_excerpt(i_transformer)  # noqa
            self.load_config(i_transformer, trace_dict)
            trace_dict['meas_dict'] = self.get_meas_dict(i_transformer)
        # update with transformer dict
        trace_dict.update(i_transformer.trace_dict)
        # update with test_run info, with priority over transformer
        self.update_with_test_run_info(trace_dict, test_run)
        # update with the collected trace metadata
        trace_dict.update(self.get_metadata(i_transformer))
        trace_dict['i_settings'] = self.inst_dict
        # build transmitter to return and eventually transmit trace
        my_transmitter = transmitters.get_transmitter(
            i_transformer, trace_dict, ses)
        # if cloud capture then transmit configuration for server db storage
        if test_run['hybrid'] or test_run['autoset']:
            my_transmitter.transmit_config()

        return my_transmitter


