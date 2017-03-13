"""Play With Docker Client - Status Command."""


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


class Info(Base):
   
        

    def run(self):

        if self.options["-d"] == True:
            print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))



        if self.utils.pwd_init() == self.utils.ko:
            return self.utils.ko

        self.utils.print_welcome()
        return self.utils.ok
