#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time

YELLOW = '1;33;40'
GREEN = '1;32;40'
RED = '1;31;40'


def cprint(msg, color=None):
    if not color:
        sys.stdout.write('{msg}'.format(c=color, msg=msg))
    else:
        sys.stdout.write('\x1b[{c}m{msg}\x1b[0m'.format(c=color, msg=msg))


def typewrite(msg, delay, color=None):
    for char in msg:
        cprint(char, color)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(os.linesep)


def log(msg, delay=0.3, color=YELLOW):
    cprint(msg, color)
    sys.stdout.write(os.linesep)
    sys.stdout.flush()
    time.sleep(delay)


def narrator(msg, delay=0.05):
    typewrite(msg, delay)
    time.sleep(1)


def cmd(msg, delay=0.02):
    typewrite(msg, delay, RED)
    time.sleep(0.1)


def pause(delay=1):
    time.sleep(delay)


def clear():
    os.system('clear')


def run():
    styles = {
        'type': narrator,
        'log': log,
        'cmd': cmd,
    }

    commands = {'pause': pause,
                'clear': clear}

    style = typewrite
    command = None
    delay = None
    with open('people/carlos.txt') as fn:
        for line in (line.strip() for line in fn.readlines()):
            # Parse styles
            if line.startswith('#'):
                args = line.split('#')
                if len(args) > 1 and styles.get(args[1]):
                    style = styles.get(args[1])
                    if len(args) > 2:
                        delay = float(args[2])
                    else:
                        delay = None
                continue
            # Parse commands
            if line.startswith('>'):
                args = line.split('>')
                if len(args) > 1 and commands.get(args[1]):
                    command = commands.get(args[1])
                    command()
                continue

            if not delay:
                style(line)
            else:
                style(line, delay)

run()
