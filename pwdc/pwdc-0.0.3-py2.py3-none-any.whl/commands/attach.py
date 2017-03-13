"""Play With Docker Client - attach Command."""


from json import dumps
from .base import Base



import os
import sys

import requests

import yaml
from datetime import date, time, datetime, timedelta

from pprint import pprint
import logging
import re
from subprocess import Popen, PIPE
import click

from .. import utils


def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False   



class Create(Base):


    def attach_session(self):
        self.utils.blue("- attach_session")

        if self.options["--session_id"] != "":
            print "Attach Session " + self.options["--session_id"]
            self.utils.session['id'] = self.options["--session_id"]
            pprint (self.utils.session)
            res = self.utils.write_session()
            assert res == self.utils.ok
        return self.utils.ok



    def run(self):

        if self.options["-d"] == True:
            print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))

        self.utils.ping()
    
        if (self.utils.read_session() == self.utils.ok) and (self.utils.check_session() == self.utils.ok):
            self.utils.debug("green", "you already have a session : " + self.utils.session['id'] + " in file : " + self.utils.session_file)
            if self.utils.options["-d"] == True:
                pprint (self.utils.session)
                if not confirm("Do you want to erase your session ?", False):
                    return self.utils.ko

        self.utils.rm_session()

        self.attach_session()

        self.utils.print_welcome()
                    

