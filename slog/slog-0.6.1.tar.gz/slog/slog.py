#!/usr/bin/python
# coding=utf8

import logging

from inspect import currentframe, getframeinfo
from time import strftime, sleep
from termcolor import colored

def ct():
    return strftime('%Y-%m-%d %H:%M:%S')

class Slog(object):
    def __init__(self, logfile=None, loglvl=3):
        if logfile is not None:
            self.logfile = open(logfile, 'w+')
        else:
            self.logfile = None
        if 0 <= loglvl <= 5:
            self.loglvl = loglvl
        else:
            self.loglvl = 3
        self.messageMade = False

    def get_file_and_lineno(self):
        return (currentframe().f_back.f_back.f_back.f_code.co_filename,
                currentframe().f_back.f_back.f_back.f_lineno)

    def __del__(self):
        if self.logfile:
            self.logfile.close()

    def makeMessage(self, level, message, color):
        self.messageMade = True
        fn, ln = self.get_file_and_lineno()
        fn = fn.split('/')[-1]
        if level != 'ok':
            return [
                    str(ct()) + ' || [ ' + level.upper() + ' ] ' + colored('⬢', color) +' (\033[1m{0}:{1}\033[0m)\t'.format(fn, ln) + message,
                    str(ct()) + ' || [ ' + level.upper() + ' ] (\033[1m{0}:{1}\033[0m)\t'.format(fn, ln) + message]
        else:
            return [
                    str(ct()) + ' || [  '+ level.upper() +'  ] ' + colored('⬢', color) +' (\033[1m{0}:{1}\033[0m)\t'.format(fn, ln) + message,
                    str(ct()) + ' || [  '+ level.upper() +'  ] (\033[1m{0}:{1}\033[0m)\t'.format(fn, ln) + message]

    def slogPrint(self, message, level, writem):
        if level <= self.loglvl:
            if 't' in writem:
                print(message[0])
            if self.logfile and 'f' in writem:
                self.logfile.write(message[1] + '\n')

    def ok(self, message, writem='ft'):
        message = self.makeMessage('ok', message, 'green')
        self.slogPrint(message, 5, writem)

    def info(self, message, writem='ft'):
        message = self.makeMessage('info', message, 'blue')
        self.slogPrint(message, 4, writem)

    def warn(self, message, writem='ft'):
        message = self.makeMessage('warn', message, 'yellow')
        self.slogPrint(message, 3, writem)

    def fail(self, message, writem='ft'):
        message = self.makeMessage('fail', message, 'red')
        self.slogPrint(message, 2, writem)

    def crit(self, message, writem='ft'):
        message = self.makeMessage('crit', message, 'magenta')
        self.slogPrint(message, 1, writem)

    def write(self, message, level=3, color='blue', writem='ft'):
        self.slogPrint(message, level, writem)
