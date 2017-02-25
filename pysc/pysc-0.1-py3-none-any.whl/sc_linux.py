import os
import signal
from subprocess import check_call, call, list2cmdline


__all__ = [
    'create',
    'delete',
    'start',
    'stop',
    'event_stop',
]


def create(service_name, cmd, username=None, password=None):
    sv_dir = '/etc/sv/{}'.format(service_name)
    if not os.path.exists(sv_dir):
        os.makedirs(sv_dir)

    run_path = '{}/run'.format(sv_dir)
    cmd = list2cmdline(cmd)
    with open(run_path, 'w') as f:
        f.write('#!/bin/sh\n\nexec {}'.format(cmd))

    check_call(['chmod', '+x', run_path])
    call(['ln', '-s', sv_dir, '/etc/service/{}'.format(service_name)])


def delete(service_name):
    sv_dir = '/etc/sv/{}'.format(service_name)
    service_dir = '/etc/service/{}'.format(service_name)
    for path in [sv_dir, service_dir]:
        if os.path.exists(path):
            call(['rm', '-r', path])


def start(service_name):
    call(['/usr/bin/sv', 'start', service_name])


def stop(service_name):
    call(['/usr/bin/sv', 'stop', service_name])


def event_stop(close_func):
    def signal_handler(signal, frame):
        close_func()
    signal.signal(signal.SIGTERM, signal_handler)
