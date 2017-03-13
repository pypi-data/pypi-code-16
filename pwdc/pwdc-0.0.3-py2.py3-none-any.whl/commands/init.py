"""Play With Docker Client - Init Command."""
""" used to setup the PWD url for your pwdc client """

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


class Init(Base):
   
        

    def run(self):

        if self.options["-d"] == True:
            print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))

        self.utils.write_config_file()
        self.utils.green("pwd_url is " + self.utils.pwd_url)

