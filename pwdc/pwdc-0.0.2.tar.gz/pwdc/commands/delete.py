"""Play With Docker Client - Delete Command."""


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


class Delete(Base):
   
        

    def delete_session(self):
        global session
        self.utils.blue("- delete_session")
        resp = requests.delete( self.utils._url("/sessions/{:s}".format(self.utils.session['id'])) )
        if resp.status_code != 204:
            if resp.status_code  == 404:
                print ("Session {:s} does not exist".format(self.utils.session['id']))
                return self.utils.ko
            else:
                print "Delete Session error"
                raise BaseException('Delete ' + self.utils.pwd_url + "/sessions/" + self.utils.session["id"])
        self.utils.rm_session()
        return self.utils.ok


    def run(self):

        if self.options["-d"] == True:
            print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))

        if self.utils.pwd_init() == self.utils.ko:
            return self.utils.ko

        if not self.delete_session():
               self.utils.red("Error Deleting session")
               return self.utils.ko
        self.utils.blue("Session deleted, unset DOCKER_HOST and unset DOCKER_MACHINE_NAME")
        return self.utils.ok

