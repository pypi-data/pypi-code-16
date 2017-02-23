#!/usr/bin/env python

"""
unify virtual filesystems
"""

import argparse
import getpass
import os
import socket
import subprocess
import sys
from martini.config import ConfigMunger
from pkg_resources import iter_entry_points
from pprint import pprint
from .utils import home
from .utils import ip_addresses


def make_config(filename):
    # XXX needed?
    raise NotImplementedError('Need to specify a config file, like\n~/.silvermirror')


def read_config(filename):
    """read configuration `filename`"""

    config = ConfigMunger(filename).dict()

    ### main configuration
    main = config.pop('::SilverMirror::', {})
    if not main.get('basedir'):
        main['basedir'] = home()
    main['ignore'] = main.get('ignore', '').split() # patterns to ignore - not used
    main['hosts'] = main.get('hosts', '').split()
    main['timeout'] = float(main.get('timeout', '10.'))

    # password prompt
    truth = dict([(str(i).lower(), i) for i in (True, False)])
    password = main.get('password', 'true')
    try:
        main['password'] = truth[password.lower()]
    except KeyError:
        raise KeyError("password must be True or False (You gave: '%s')" % password)

    ### resources
    for resource in config:

        # directory of resource
        directory = config[resource].get('directory', resource)
        if not os.path.isabs(directory):
            # XXX note: absolute directories will not work for now
            # XXX so....don't do this!
            directory = os.path.join(main['basedir'], directory)
        config[resource]['directory'] = directory.rstrip(os.path.sep)

        # per-resource files to ignore
        # XXX  regexps for now (see `man unison`)
        # - this is bad as whitespace patterns cannot be ignored
        ignore = main['ignore'][:]
        if config[resource].has_key('ignore'):
            ignore += config[resource]['ignore'].split()
        config[resource]['ignore'] = ignore

    ###
    config = { 'main': main, 'resources': config }
    return config

def unify(conf, _resources, test=False, verbose=True, notification_prefix='\n*** SilverMirror; '):
    """unify virtual filesystems given configuration"""

    # TODO: -> OO

    # log function
    def log(message):
        if verbose:
            print ("%s%s" % (notification_prefix, message))

    # passwords
    pw = {}

    # determine hosts to sync with
    hosts = conf['hosts']
    addresses = ip_addresses().values()
    hosts = hosts.difference(addresses) # don't sync with self
    _hosts = []
    for host in hosts:
        s = socket.socket()
        s.settimeout(conf['main']['timeout'])
        if test:
            print ('Resolving %s' % host)
        try:
            s.connect((host, 22))
            s.close()
        except (socket.gaierror, socket.timeout, socket.error):
            continue
        _hosts.append(host)
    hosts = _hosts
    log("Hosts:\n%s" % '\n'.join(hosts))
    if not hosts:
        raise AssertionError("No hosts specified")

    if conf['main']['password']:
        for host in hosts:
            pw[host] = getpass.getpass('Enter password for %s: ' % host)
    # TODO: ensure that the hosts are resolvable
    # XXX: hosts should actually be manageable on a per-resource basis

    ### determine resources to sync
    cwd = os.path.realpath(os.getcwd())
    resources = conf['resources']
    if 'all' not in _resources:
        if _resources:
            resources = dict([(key, value) for key, value in resources.items()
                              if key in _resources])
        else:
            for key, value in resources.items():
                directory = os.path.realpath(value['directory']) + os.sep
                if (cwd + os.sep).startswith(directory):
                    resources = { key: value }
                    break
    if test:
        log("Resources:\n")
        pprint(resources)

    # choose reflector backend
    reflectors = dict([(i.name, i.load()) for i in iter_entry_points('silvermirror.reflectors')])
    reflector = reflectors['unison']() # only one right now

    # sync with hosts
    try:
        os.chdir(conf['main']['basedir'])
        for index, resource in enumerate(resources):

            # echo resource
            log("syncing:'%s' [%d/%d]" % (resource, index+1, len(resources)))

            # loop over hosts
            for host in hosts:
                reflector.sync(host, resource, resources[resource]['ignore'], pw.get('host'), test)
    finally:
        os.chdir(cwd)

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--config')
    parser.add_argument('-H', '--host', dest='hosts', action='append',
                        help="hosts to sync with")
    parser.add_argument('--no-password', dest='password',
                        action='store_false', default=True)
    parser.add_argument('--test', dest='test',
                        action='store_true', default=False)
    parser.add_argument('-v', '--verbose',
                        action='store_true', default=False)
    parser.add_argument('resources', nargs='*',
                        help="resources to sync, or all if omitted")
    options = parser.parse_args(args)


    # configuration
    user_conf = os.path.join(home(), '.silvermirror')
    if options.config:
        if not os.path.exists(options.config):
            parser.error("Configuration file '" + options.config + "' does not exist")
        conf = read_config(options.config)
    else:
        for i in (user_conf, '/etc/silvermirror'):
            if os.path.exists(i):
                conf = read_config(i)
                break
        else:
            conf = make_config(user_conf)

    # fix up configuration from command line options
    conf['hosts'] = set(options.hosts or conf['main']['hosts'])
    conf['main']['password'] = options.password and conf['main']['password']

    # mirror all the things
    unify(conf, args, options.test)

if __name__ == '__main__':
    unify()
