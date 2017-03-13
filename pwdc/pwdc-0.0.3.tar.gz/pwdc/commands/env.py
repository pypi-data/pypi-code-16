"""Play With Docker Client - Create Command."""


from json import dumps
from .base import Base


import os
import sys

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.append(vendor_dir)

import requests
import json
import yaml
from datetime import date, time, datetime, timedelta

from pprint import pprint
import logging
import re
from subprocess import Popen, PIPE
import click

from .. import utils



class Env(Base):


    def run(self):

        if self.options["-d"] == True:
            print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))


        if self.options["-u"] == True:
            print ('unset DOCKER_HOST')
            print ('unset DOCKER_MACHINE_NAME')
            sys.exit(0)

#j'utilise pas le self.utils.pwd_init() car je veux pas de print (ca perturbe le eval)

        if not self.utils.read_session():
            self.utils.red("No PWD Session, check --session_file parameter")
            return self.utils.ko

        if self.utils.check_session() == self.utils.ko:
            self.utils.red("Your session has been deleted, please retry now")
            return self.utils.ko

#            raise RuntimeError("You must create a session")

        if 'ip1' in self.utils.session:
            print ('export DOCKER_HOST="tcp://pwd' + self.utils.session["ip1"].replace(".", "_") + '-2375.' + self.utils.pwd_dns + ':80"')
            print ('export DOCKER_MACHINE_NAME="'+self.utils.session['id']+'-'+self.utils.session["ip1"]+'"')
            return self.utils.ok
        else:
            pprint (self.utils.session)
            raise RuntimeError("ip1 does not exists in your PWD Session file.. " + self.utils.session_file)


