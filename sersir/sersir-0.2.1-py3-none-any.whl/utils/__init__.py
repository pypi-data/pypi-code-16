"""Provide helper utilities"""
import os
import socket
import subprocess
import time

import logging

logger = logging.getLogger(__name__)


def ping(host, timeout=1):
    """Test if a host responds to a network ping"""
    # Call system executable "ping"
    return_code = subprocess.call(['ping', '-c', '1', '-W', str(timeout), host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    logger.debug('Return code of ping command to host %s is %s', host, return_code)

    if return_code == 0:
        logger.debug('Host is reachable via network.')
    else:
        logger.error('Host is unreachable via network.')
        logger.error('Exiting because host is unreachable.')

        raise RuntimeError('Host {host} not available'.format(host=host))


class AuditLog:
    """
    AuditLog Class

    This class generates a persistent log of important events in the program cycle
    and converts them into human and machine readable log files.
    """

    AUDIT_FORMAT = "{timestamp} {hostname}({pid}) {event_type} {name}\n"
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %z"

    EVENT_TYPES = [
        'NEW_FAILED',
        'GOOD_AGAIN',
        'STARTED',
        'STOPPED'
    ]

    # Constructor of the AuditLog class
    def __init__(self, audit_log_file):
        self.audit_log_file = audit_log_file
        self.pid = os.getpid()
        self.hostname = socket.gethostname()

    def write(self, event_type, name):
        with open(self.audit_log_file, mode='a') as file:
            file.write(
                self.AUDIT_FORMAT.format(
                    timestamp=time.strftime(self.TIMESTAMP_FORMAT),
                    hostname=self.hostname,
                    pid=self.pid,
                    event_type=event_type,
                    name=name,
                )
            )


class Map(dict):
    """
    This class implements a dict which let you access
    the data also via dict.name
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    self[key] = value

        if kwargs:
            for key, value in kwargs.items():
                self[key] = value

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]
