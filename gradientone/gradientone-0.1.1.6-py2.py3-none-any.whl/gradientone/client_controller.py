#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import collections
import importlib
import imp
import json
import logging
import os
import pkgutil
import psutil
import requests
import subprocess
import sys
import time
import multiprocessing as multi
from configparser import ConfigParser
from types import ModuleType
from pkg_resources import DistributionNotFound, get_distribution
from os.path import expanduser
from subprocess import Popen, PIPE


cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']
BASE_URL = "https://" + COMMON_SETTINGS['DOMAIN']
GIT_DIR = 'gradientone'
SECS_BTW_UPDATE_CHECKS = 10
HOME = expanduser("~")
DEFAULT_PYTHONPATH = HOME + '/.local/lib/python2.7/site-packages'
PREFIX = HOME + '/.local'


class ClientController(object):
    """Handles running and updating the client"""
    def __init__(self, pkg='gradientone', version='0.1.1.2'):
        self.get_logger()
        self.logger.info("Updating to version: %s" % version)
        self.pip_target = self.get_pip_target()
        self.pip_install(pkg, version)
        self.og_client_name = pkg
        self.og_version = version
        self.version = version
        self.prev_version = version
        self.client_name = pkg
        self.client_module = G1Client(pkg).client_module
        self.config_gets_active = False
        self.health_posts_active = False
        self.g1_modules = ['']

    def get_logger(self, log_filename='client_controller.log'):
        self.logger = logging.getLogger('ClientController')
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)
        # create logging handlers
        console_handler = logging.StreamHandler()  # by default, sys.stderr
        file_handler = logging.FileHandler(log_filename)
        # set logging levels
        console_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
        # add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        return self.logger

    def get_pip_target(self):
        try:
            py_path = os.environ['PYTHONPATH'].split(os.pathsep)
        except KeyError:
            py_path = []
        if not py_path:
            self.logger.warning("No python path found. Adding default: %s"
                                % DEFAULT_PYTHONPATH)
            sys.path.append(DEFAULT_PYTHONPATH)
            py_path.append(DEFAULT_PYTHONPATH)
        self.logger.info("PYTHONPATH is %s" % py_path)
        self.logger.info("Returning pip target as %s" % py_path[0])
        return py_path[0]

    def active_pid(self, pid):
        """ Check if active unix pid. """
        if psutil.pid_exists(pid):
            return True
        else:
            self.logger.info("The process with pid %s does not exist" % pid)
            return False

    def start_config_gets(self):
        cfg_gets = self.client_module.gateway_client.config_gets
        config_gets_ps = multi.Process(target=cfg_gets)
        config_gets_ps.start()
        with open("config_gets.pid", "w") as f:
            f.write(str(config_gets_ps.pid))
        with open("config_gets.pid", "r") as f:
            config_gets_pid = int(f.read())
        self.config_gets_active = self.active_pid(config_gets_pid)

    def start_health_posts(self):
        health_posts = self.client_module.gateway_client.health_posts
        health_posts_ps = multi.Process(target=health_posts)
        health_posts_ps.start()
        with open("health_posts.pid", "w") as f:
            f.write(str(health_posts_ps.pid))
        with open("health_posts.pid", "r") as f:
            health_posts_pid = int(f.read())
        self.health_posts_active = self.active_pid(health_posts_pid)

    def stop_health_posts(self):
        try:
            with open("health_posts.pid", "r") as f:
                health_posts_pid = int(f.read())
            p = psutil.Process(health_posts_pid)
            p.terminate()
        except psutil.NoSuchProcess:
            self.logger.info("No health posts to stop")
        except Exception:
            self.logger.warning("Unexpected exception stopping health posts",
                                exc_info=True)

    def stop_config_gets(self):
        try:
            with open("config_gets.pid", "r") as f:
                config_gets_pid = int(f.read())
            p = psutil.Process(config_gets_pid)
            p.terminate()
        except psutil.NoSuchProcess:
            self.logger.info("No config gets to stop")
        except Exception:
            self.logger.warning("Unexpected exception stopping config gets",
                                exc_info=True)

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
        self.logger.info("Checking counter_file")
        with open("counter_file.txt", "r") as f:
            filestr = f.read()
        if filestr == last_update:
            self.logger.warning("No new file update..." + filestr)
        else:
            self.logger.info(filestr)
        return ps1, filestr  # filestr becomes the new last_update

    def run(self, seconds_btw_updates=SECS_BTW_UPDATE_CHECKS):
        """Runs the nanny

        ps1 - the config checking process, this gets updated if
              check_counter_file decides it needs to restart ps1
        sec_btw_updates - the grace period between updates that the
                          nanny allows the config runner process.
                          Defaults to 600 secs (10 mins)
        """
        self.start_client()
        while True:
            time.sleep(seconds_btw_updates)
            self.check_if_requests_active()
            self.check_for_updates()

    def set_version(self, package='gradientone', version=''):
        """Sets current and previous version"""
        if not version:
            version = self.get_version(package)
        if self.version == version:
            msg = ("Setting v-%s matches current v-%s. Backup stays as v-%s"
                   % (version, self.version, self.prev_version))
            self.logger.info(msg)
        else:
            self.prev_version = self.version
            msg = ("New v-%s replacing v-%s. The backup is now: v-%s"
                   % (version, self.version, self.prev_version))
            self.logger.info(msg)
            self.version = version

    def get_pip_show_version(self, package='gradientone'):
        """Gets version by parsing pip output"""
        pip_show_pkg = ['pip', 'show', package]
        output = Popen(pip_show_pkg, stdout=PIPE).communicate()[0]
        lines = output.split('\n')
        version = ""
        for line in lines:
            if line.startswith("Version:"):
                version = line.split(':')[1].strip()
        return version

    def pip_install(self, pkg_name='', version=''):
        if not pkg_name:
            pkg_name = self.client_name
        pip_args = ['install', '--user', '--upgrade']
        if version:
            self.logger.info("Installing version: %s" % version)
            pkg_string = pkg_name + '==' + str(version)
            pip_args.append(pkg_string)
        else:
            msg = "No version given. Simply installing " % pkg_name
            self.logger.info(msg)
            pip_args.append(pkg_name)
        cmd = 'pip ' + ' '.join(pip_args)
        self.logger.info("Making subprocess.call with %s" % cmd)
        subprocess.call(cmd, shell=True)

    def reload(self, pkg_name='', is_rollback=False, og_install=False):
        if not pkg_name:
            pkg_name = self.client_name
        if self.reload_by_name(pkg_name):
            self.logger.info("Successfully reloaded %s" % pkg_name)
        else:
            if og_install:
                msg = ("Unable to reload original client! This process will "
                       "continue polling for gateway client software updates."
                       "However, no gateway client that is running may not "
                       "have the latest update running. Restart required.")
                self.logger.warning(msg)
            elif is_rollback:
                self.install_original()
                self.start_client(og_install=True)
            else:
                response = self.rollback()
                if "Success" in response:
                    self.start_client(is_rollback=True)
                    return
                else:
                    self.install_original()
                    self.start_client(og_install=True)

    def pip_uninstall(self, pkg_name=''):
        if not pkg_name:
            pkg_name = self.client_name
        subprocess.call('pip uninstall', shell=True)

    def install_original(self):
        self.pip_install(self.og_client_name, self.og_version)
        if self.verify_version_info(self.og_client_name, self.og_version):
            msg = ("Successfuly installed original client: %s v-%s"
                   % (self.og_client_name, self.og_version))
            self.logger.info(msg)
        else:
            msg = ("Failed to install original client: %s v-%s"
                   % (self.og_client_name, self.og_version))
            self.logger.warning(msg)
        return msg

    def update(self, pkg_name='gradientone', version='',
               force_uninstall=False, is_rollback=False):
        self.logger.info("Current client version: %s" % self.version)
        if force_uninstall:
            self.pip_uninstall(pkg_name)
        self.pip_install(pkg_name, version)
        if self.verify_version_info(pkg_name, version):
            return "Success! Current version is v-%s" % version
        elif is_rollback:
            self.logger.warning("Rollback update failed. Installing original")
            return self.install_original()
        else:
            msg = "Update failed"
            self.logger.warning(msg)
            return msg

    def verify_version_info(self, pkg_name, version=''):
        self.logger.warning("Verifying version update...")
        v_from_pip_show = self.get_pip_show_version(pkg_name)
        if v_from_pip_show != version:
            msg = ("Verification of v-%s failed. Current version is: v-%s"
                   % (version, v_from_pip_show))
            self.logger.warning(msg)
            return None
        else:
            self.logger.warning("Verification of current client v-%s. Success!"
                                % v_from_pip_show)
            self.set_version(pkg_name, v_from_pip_show)
            return True

    def process_update_cmd(self, data={'package': 'gradientone'}):
        """Processes update command from server

        If the update succeeds then the new client is started.
        If the update fails then try a resinstall of current version
        If reinstall of current fails, try rollback to previous
        If rollback to previous fails, try install of original
        and try to start client regardless of og_install result.
        """
        update = collections.defaultdict(str, data)
        if update['version'] == self.version:
            msg = ("Server version:%s matches client. No action necessary"
                   % update['version'])
            self.logger.info(msg)
            return
        # stop client during update process
        self.stop_client()
        response = self.update(pkg_name=update['package'],
                               version=update['version'])
        if 'Success' in response:
            self.logger.info("Update: %s" % response)
            self.start_client()
        else:
            # If the update failed. Reinstall current version
            self.logger.info("Trying re-install of version: %s" % self.version)
            self.pip_install(self.client_name, self.version)
            # Verify the reinstall. If failed, rollback to previous v.
            if self.verify_version_info(self.client_name, self.version):
                self.start_client()
            else:
                response = self.rollback()
                if "Success" in response:
                    self.logger.info("Rollback: %s" % response)
                    self.start_client(is_rollback=True)
                else:
                    self.logger.info("Rollback failed. Installing original")
                    response = self.install_original()
                    self.start_client(og_install=True)

    def reload_by_name(self, modname):
        """Safe reload(module) that accepts strings

        Allows str, unicode string, or ModuleType
        """
        if isinstance(modname, str):
            self.logger.info("Getting module from str: %s" % modname)
            self.client_module = G1Client(modname).client_module
        elif isinstance(modname, ModuleType):
            self.logger.warning("Assigning modname as module")
            self.client_module = modname
        elif isinstance(modname, unicode):
            self.logger.info("Getting module from unicode: %s" % modname)
            try:
                self.client_module = G1Client(str(modname)).client_module
            except Exception as e:
                self.logger.warning("Unexpected reload err:%s " % e)
                return None
        else:
            self.logger.warning("Unexpected modname type:%s" % type(modname))
            return None
        self.logger.info("Reloading module %s" % self.client_module)
        try:
            imp.reload(self.client_module)
            imp.reload(self.client_module.gateway_helpers)
            imp.reload(self.client_module.gateway_client)
            return True
        except Exception as e:
            self.logger.warning("Exception during reload: %s" % e)
            return None

    def check_for_updates(self):
        session = requests.session()
        while True:
            try:
                url = BASE_URL + '/client_updates'
                msg = "Current v " + self.version + " checking:" + url
                self.logger.info(msg)
                response = session.get(url)
                data = json.loads(response.text)
                self.logger.info("/client_updates response: %s" % data)
                if data == 'restart':
                    self.restart_client()
                elif data == 'stop':
                    self.stop_client()
                elif data == 'start':
                    self.start_client()
                elif isinstance(data, dict):
                    self.process_update_cmd(data)
            except Exception:
                self.logger.error("Exception in pulling code", exc_info=True)
            time.sleep(SECS_BTW_UPDATE_CHECKS)

    def rollback(self):
        self.logger.info("Rolling back to v-%s" % self.prev_version)
        self.stop_client()
        response = self.update(pkg_name=self.client_name,
                               version=self.prev_version,
                               is_rollback=True)
        return response

    def start_client(self, is_rollback=False, og_install=False):
        self.logger.info("Starting client: %s v-%s"
                         % (self.client_name, self.version))
        self.reload(self.client_name, is_rollback, og_install)
        try:
            self.start_config_gets()
            self.start_health_posts()
        except Exception:
            self.logger.error("Exception in starting client", exc_info=True)
            if og_install:
                msg = ("Unable to start original client! This process will "
                       "continue polling for gateway client software updates."
                       "However, no gateway client is running until a "
                       "successful update happens.")
                self.logger.warning(msg)
            elif is_rollback:
                self.install_original()
                self.start_client(og_install=True)
            else:
                self.rollback()
                self.start_client(is_rollback=True)

    def stop_client(self):
        self.logger.info("Stopping client processes")
        try:
            self.stop_config_gets()
            self.stop_health_posts()
        except Exception:
            self.logger.error("Exception in stopping client", exc_info=True)

    def restart_client(self):
        self.logger.info("Preparing to restart client....")
        self.stop_client()
        self.start_client()

    def kill_proc_tree(pid, including_parent=False):
        parent = psutil.Process(pid)
        for child in parent.get_children(recursive=True):
            child.kill()
        if including_parent:
            parent.kill()

    def log(self, msg):
        self.logger.info(msg)

    def get_dist_version(self, package='gradientone'):
        """Gets version using pgk_resources"""
        try:
            _dist = get_distribution(package)
        except DistributionNotFound as e:
            self.version = 'Please install %s' % package
            self.logger.warning("DistributionNotFound: %s" % e)
        except Exception as e:
            self.logger.warning("Exception in get_distribution, %s" % e)
            self.version = 'No version info'
        else:
            self.version = _dist.version
            self.logger.warning("_dist.version: %s" % _dist.version)
        return self.version

    def rreload(self, package, parent_pkg='gradientone'):
        """Recursively reload packages."""
        self.logger.info("rreload on %s" % package)
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
            self.logger.info("Found submodule %s (is a package: %s)"
                             % (modname, ispkg))
            modname = parent_pkg + "." + modname
            self.logger.info("modname: %s" % modname)
            try:
                module = importer.find_module(modname).load_module(modname)
                if ispkg:
                    self.rreload(module, parent_pkg=modname)
                else:
                    self.simple_reload(module)
            except Exception as e:
                msg = "load module %s exc: %s" % (modname, e)
                self.logger.info(msg)


class G1Client(object):
    def __init__(self, pkg_name='gradientone'):
        self.client_module = self.get_module(pkg_name)

    def get_module(self, module_name):
        if module_name in sys.modules:
            return sys.modules[module_name]
        else:
            return importlib.import_module(module_name)


class UpdateException(Exception):
    def __init__(self, message, errors):
        super(UpdateException, self).__init__(message)
        self.errors = errors


pid = str(os.getpid())
pidfile = "/tmp/mydaemon.pid"

if __name__ == "__main__":
    f = open(pidfile, 'w')
    f.write(pid)
    f.close()
    try:
        ctrl = ClientController()
        ctrl.run()
    finally:
        os.unlink(pidfile)


# cron job that logs status and restarts if failed
# * * * * * ps up `cat /tmp/mydaemon.pid ` >/dev/null && echo "Working at: $(date)" >> /tmp/debug.log || echo "Restart at: $(date)" >> /tmp/debug.log || echo "Failed Restart at: $(date)" >> /tmp/debug.log  # noqa
# * * * * * ps up `cat /tmp/mydaemon.pid ` >/dev/null || /usr/local/bin/python [REPLACE WITH PATH TO THIS FILE] 2> /tmp/err.log  # noqa
# 0 0 */3 * * > /tmp/debug.log
