#!/usr/bin/env python


"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import collections
import datetime
import json
import multiprocessing as multi
import os
try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

import psutil
import time
import traceback
from configparser import ConfigParser
from subprocess import Popen
import requests
import gateway_helpers
import misc_scope
import tek_grl_configs
import test_runners
from device_drivers import usb_controller

#from matlab_conversion import process_conversion_request
import schema_forms

cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']

### REMOVE THIS BEFORE IT GOES TO THE CUSTOMER
try:
    from raven import Client
    SENTRY_CLIENT = Client(cfg['client']['SENTRY'])
except Exception:
    SENTRY_CLIENT = gateway_helpers.MySentry()
###




INSTRUMENTS = gateway_helpers.get_usbtmc_devices()




SOFTWARE_VERSION = "skywave-version-1.05-3"
SECONDS_BTW_HEALTH_POSTS = 15
CLIENT_ID = 'ORIGINAL'
SAMPLE_FILE = 'MDO30121M.txt'
if COMMON_SETTINGS['DOMAIN'].find("localhost") == 0 or COMMON_SETTINGS['DOMAIN'].find("127.0.0.1") == 0:
    BASE_URL = "http://"+COMMON_SETTINGS['DOMAIN']
else:
    BASE_URL = "https://" + COMMON_SETTINGS['DOMAIN']
CONFIG_URL = (BASE_URL + '/testplansummary/' +
              COMMON_SETTINGS['COMPANYNAME'] + '/' +
              COMMON_SETTINGS['HARDWARENAME'])


logger = gateway_helpers.get_logger(
    log_filename=CLIENT_SETTINGS['DEFAULT_LOGFILE'])


class ConfigManager(object):
    """Manages configs for instruments from the server"""
    def check_config_url(self):
        """polls the configuration URL for a test run object"""
        config_url = (BASE_URL +
                      "/testplansummary/" + COMMON_SETTINGS['COMPANYNAME'] +
                      '/' + COMMON_SETTINGS['HARDWARENAME'])
        headers = gateway_helpers.get_headers()
        ses = requests.session()
        response = ses.get(config_url, headers=headers)
        if response.status_code == 401:
            headers = gateway_helpers.get_headers(refresh=True)
            response = ses.get(config_url, headers=headers)
        if response:
            setup = collections.defaultdict(int)
            setup_info = json.loads(response.text)
            setup.update(setup_info)
            self.process_response(setup, ses)
        else:
            logger.error("No response from server")

    def run(self):
        """Runs the config manager indefinitely"""
        update_timer = 0
        while True:
            try:
                self.check_config_url()
            except Exception as e_msg:
                logger.warning("check_config_url exception", exc_info=True)
                SENTRY_CLIENT.captureException("check_config_url exception "+
                                               str(e_msg))
            time.sleep(1)
            update_timer += 1
            if update_timer == 10:  # updates counter file 10sec intervals
                update_timer = 0
                update_counter_file()

    def process_response(self, setup, ses):
        """Processes response from server to config get requests"""
        logger.debug("Setup received: %s" % setup)
        if setup['test_run']:
            logger.info("Run request received: %s" % setup['test_run'])
            self.process_test_run(setup, ses)
        # most commands will be test runs like above
        # special commands and continue commands below
        elif 'check_scope' in setup and setup['check_scope']:
            try:
                instrument_type = setup['instrument_type']
                scope_info = misc_scope.check_scope(instrument_type)
            except Exception as e_msg:
                logger.error(traceback.format_exc())
                SENTRY_CLIENT.captureException(str(e_msg))
                scope_info = None
            finally:
                gateway_helpers.post_alert(ses, scope_info)
        elif 'special_command' in setup:
            self.process_special_command(ses, setup)
        # If the response from the server has no orders or commands
        else:
            logger.info("No run order; Time:" + str(datetime.datetime.now()) +
                        "; Gateway:" + COMMON_SETTINGS['HARDWARENAME'] +
                        "; Company:" + COMMON_SETTINGS['COMPANYNAME'] +
                        "; Domain:" + COMMON_SETTINGS['DOMAIN'] +
                        "; Version:" + SOFTWARE_VERSION)

    def process_test_run(self, setup, ses):
        """Processes test_run, checking config and calling TestRunner"""
        test_run = setup['test_run']
        logger.info("processing run request: %s" % test_run)
        config = setup['config']
        if not config:
            logger.warning("Run request missing config data")
            return

        test_runner = test_runners.TestRunner(setup, ses)
        test_runner.run_the_setup()

    def process_special_command(self, session, setup):
        """Runs special commands not associated with an instrument run"""
        spc = setup['special_command']
        logger.info("Special command found: %s" % spc)
        if spc == 'reset' or spc == 'check':
            misc_scope.check_or_reset(session, spc, setup['instrument_type'])
        elif spc == 'reset_usb':
            gateway_helpers.reset_device_with_tag()
        elif spc == 'UsbRawInputCommand':
            usb_contr = usb_controller.UsbController()
            instr = usb_contr.get_instrument(setup['mnf_id'], setup['dev_id'])
            logger.info("issuing command %s" % setup['usb_command'])
            resp = usb_contr.ask(instr, setup['usb_command'])
            logger.info(resp)
        elif spc == 'grl-test':
            logger.info("starting grl-test")
            grl = tek_grl_configs.Grl_Test()
            resp = grl.run_grl_test()
            logger.info("grl test response: %s" % resp)
            gateway_helpers.post_alert(session, {'grl_test': resp})
        else:
            logger.warning("unknown special command: %s" % spc)
            gateway_helpers.post_alert(session, {'unknown_command': spc})


def update_counter_file():
    """Updates counter for nanny to check"""
    with open("counter_file.txt", "w") as counter_file:
        counter_file.write("Last run at %s" % str(datetime.datetime.now()))


def config_gets():
    """Starts the manager for getting and running configs"""
    update_counter_file()
    cfg_manager = ConfigManager()
    cfg_manager.run()


class HealthManager(object):
    """Manages process that posts gateway health info"""
    def post_health_data(self, session):
        """posts the health data to server for logging"""
        health_url = (BASE_URL +
                      "/testplansummary/" + COMMON_SETTINGS['COMPANYNAME'] +
                      '/' + COMMON_SETTINGS['HARDWARENAME'])
        payload = {
            "instruments": INSTRUMENTS,
            "gateway": COMMON_SETTINGS['HARDWARENAME'],
            "software": SOFTWARE_VERSION,
        }
        data = json.dumps(payload)
        logger.info("Posting to: %s with data: %s" % (health_url, data))
        gateway_helpers.authorize_and_post(session, health_url, data)

    def run(self):
        """Runs the health manager indefinitely"""
        session = requests.session()
        while True:
            try:
                self.post_health_data(session)
            except Exception as e_msg:
                logger.info("post health data exception", trace=True)
                SENTRY_CLIENT.captureException("post health data exception "+
                                             str(
                    e_msg))
            time.sleep(SECONDS_BTW_HEALTH_POSTS)


def health_posts():
    """Runs the manager that posts gateway health info"""
    with open("health_posts.pid", "w") as f:
        f.write(str(os.getpid()))
    health_manager = HealthManager()
    health_manager.run()


class GatewayManager(object):
    """Manages the gateway itself"""
    def request_commands(self):
        """Polls the command URL for a commands that control the NUC"""
        command_url = (BASE_URL +
                       "/get_nuc_commands/" + COMMON_SETTINGS['COMPANYNAME'] +
                       "/" + COMMON_SETTINGS['HARDWARENAME'] + "/" + CLIENT_ID)
        response = gateway_helpers.authorize_and_get(command_url)
        command = response.text
        if command != 'None':
            logger.info("command received: " + command)
        else:
            command = None
        return command

    def command_handler(self, config_gets, health_posts, conversion_gets):
        """Handles ad hoc commands for gateway"""
        while True:
            command = self.request_commands()
            if not command:
                log_statement = "COMMAND PROCESSOR LOG: No command at "
                log_statement += str(datetime.datetime.now())
                logger.info(log_statement)
            elif command == "start_conversion_checks":
                conversion_gets.start()
            elif command == "stop_conversion_checks":
                conversion_gets.terminate()
            elif command == "start_test_run_checks":
                config_gets.start()
            elif command == "stop_test_run_checks":
                config_gets.terminate()
            elif command == "start_health_posts":
                health_posts_ps = multi.Process(target=health_posts)
                health_posts_ps.start()
            elif command == "stop_health_posts":
                health_posts.terminate()
            elif command == "print_date":
                os.system("date")
            elif command == "get_new_client":
                new_client_url = (BASE_URL +
                                  "/get_new_client/" +
                                  COMMON_SETTINGS['COMPANYNAME'] + '/' +
                                  COMMON_SETTINGS['HARDWARENAME'])
                os.system("curl " + new_client_url + " > new_client.py")
                logger.info("new_client.py created")
            elif command == "run_new_client":
                new_client_proc = Popen(['python', 'new_client.py'])
            elif command == "stop_new_client":
                try:
                    new_client_proc.terminate()
                except Exception:
                    logger.info("unable to terminate new_client")
            time.sleep(10)


def gateway_mgmt(config_gets, health_posts, conversion_gets):
    """Runs the manager for handling commands for the gateway

    This manages commands just for the gateway and not for any
    connected instruments, devices, etc.
    """
    gateway_manager = GatewayManager()
    gateway_manager.command_handler(config_gets, health_posts, conversion_gets)


class Nanny(object):
    """Monitors gateway client and restarts if necessary

    The Nanny uses two ways of verifying the processes.

       1) It checks if the requests processes are active by checking
          if the unix pid is active.
       2) It checks if the config gets process is still updating the
          counter file. If the file is not getting updated anymore,
          then the process is likely hung up from running a config

    In either case, if a problem is detected then the process is
    restarted and the Nanny continues monitoring
    """
    def __init__(self):
        self.config_gets_active = False
        self.health_posts_active = False

    def active_pid(self, pid):
        """ Check if active unix pid. """
        if psutil.pid_exists(pid):
            return True
        else:
            logger.info("The process with pid %s does not exist" % pid)
            return False

    def start_config_gets(self):
        config_gets_ps = multi.Process(target=config_gets)
        config_gets_ps.daemon = True
        config_gets_ps.start()
        with open("config_gets.pid", "w") as f:
            f.write(str(config_gets_ps.pid))
        with open("config_gets.pid", "r") as f:
            config_gets_pid = int(f.read())
        self.config_gets_active = self.active_pid(config_gets_pid)

    def start_health_posts(self):
        health_posts_ps = multi.Process(target=health_posts)
        health_posts_ps.daemon = True
        health_posts_ps.start()
        with open("health_posts.pid", "w") as f:
            f.write(str(health_posts_ps.pid))
        with open("health_posts.pid", "r") as f:
            health_posts_pid = int(f.read())
        self.health_posts_active = self.active_pid(health_posts_pid)

    def check_if_requests_active(self):
        """Check request processes, restart if not running"""
        try:
            with open("config_gets.pid", "r") as f:
                config_gets_pid = int(f.read())
            self.config_gets_active = self.active_pid(config_gets_pid)
        except Exception:
            self.config_gets_active = False
        if not self.config_gets_active:
            self.start_config_gets()
        try:
            with open("health_posts.pid", "r") as f:
                health_posts_pid = int(f.read())
            self.health_posts_active = self.active_pid(health_posts_pid)
        except Exception:
            self.health_posts_active = False
        if not self.health_posts_active:
            self.start_health_posts()

    def check_counter_file(self, ps1, last_update):
        """Checks if the updates to the counter file

        Verifies that config check process is still updating the
        counter file. If not, then the process is most likely hung up
        and so it is terminated and a new process is started.
        """
        logger.info("Checking counter_file")
        with open("counter_file.txt", "r") as f:
            filestr = f.read()
        if filestr == last_update:
            logger.warning("No new file update..." + filestr)
            # ps1.terminate()
            # ps1 = multi.Process(name='restartConfigChecks',
            #                     target=config_gets,)
            # ps1.start()
        else:
            logger.info(filestr)
        return ps1, filestr  # filestr becomes the new last_update

    def run(self, seconds_btw_updates=600):
        """Runs the nanny

        ps1 - the config checking process, this gets updated if
              check_counter_file decides it needs to restart ps1
        sec_btw_updates - the grace period between updates that the
                          nanny allows the config runner process.
                          Defaults to 600 secs (10 mins)
        """
        while True:
            time.sleep(seconds_btw_updates)
            try:
                self.check_if_requests_active()
            except Exception as e_msg:
                SENTRY_CLIENT.captureException(e_msg)


def run_nanny():
    """Runs nanny process to monitor client"""
    client_nanny = Nanny()
    client_nanny.run()





def start_processes():
    """Kicks off all gateway client processes"""
    # config_gets_ps = multi.Process(target=config_gets,
    #                                name='get_config_manager:' +
    #                                COMMON_SETTINGS['DOMAIN'])
    # config_gets_ps.daemon = True

    # config_gets_ps.start()

    # with open("config_gets.pid", "w") as f:
    #     f.write(str(config_gets_ps.pid))
    # health_posts_ps = multi.Process(target=health_posts,
    #                                 name='health_posts:' +
    #                                 COMMON_SETTINGS['DOMAIN'])
    # health_posts_ps.daemon = True
    # health_posts_ps.start()

    # matlab conversion has been disabled for now until we can fix a scipy version.

    # args = (config_gets_ps, health_posts_ps, None)
    # gateway_mgmt_ps = multi.Process(target=gateway_mgmt, args=args,
    #                                 name='cmd_handler:' +
    #                                 COMMON_SETTINGS['DOMAIN'])
    # gateway_mgmt_ps.start()
    nanny_process = multi.Process(target=run_nanny,
                                  name='nanny_process:' +
                                  COMMON_SETTINGS['DOMAIN'])
    nanny_process.start()


pid = str(os.getpid())
pidfile = "/tmp/mydaemon.pid"

def post_config_form(instruments=None):
    if not instruments:
        instruments = INSTRUMENTS
    # upload all config forms for available instruments
    for instrument in instruments:
        if instrument in dir(schema_forms):
            FORM_DICT = getattr(schema_forms, instrument).FORM_DICT
            SCHEMA_DICT = getattr(schema_forms, instrument).SCHEMA_DICT
        else:
            FORM_DICT = "unavailable for instrument: "+instrument
            SCHEMA_DICT = {}
        # Todo: make this general to all forms
        _data = {"schema": SCHEMA_DICT, "form": FORM_DICT, "defaults": [],
                 "instrument_type": instrument}
        schema_url = urljoin(BASE_URL, "schemaform")
        headers = gateway_helpers.get_headers()
        session = requests.session()
        response = session.post(schema_url, headers=headers, data=json.dumps(_data))
        assert response.status_code == 200


def run():
    try:
        post_config_form()
    except Exception as e_msg:
        SENTRY_CLIENT.captureException(e_msg)
    logger.info("starting processes")
    start_processes()


if __name__ == "__main__":
    run()
