#!/bin/python

import os
import sys
from openedoo_script import RunServer, Manager, Shell
import unittest
import json
import shutil
from openedoo_cli import app
from openedoo_cli import bin
from utils import *

manager = Manager(app)

@manager.command
def install():
    print download()

@manager.command
def read():
    print readfile()

def main():
    manager.run()
