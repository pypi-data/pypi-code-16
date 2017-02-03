#!/bin/python

import os
import sys
from openedoo_script import RunServer, Manager, Shell
import unittest
import json
import shutil
from openedoo_core import app
from openedoo_core.bin.untar import untar_file
from utils import *


manager = Manager(app)

@manager.command
def install():
	try:
		os.makedirs("openedoo")
		os.chdir('openedoo')
		print untar_file()
	except Exception as e:
		print "folder openedoo has exist"

def main():
		manager.run()
