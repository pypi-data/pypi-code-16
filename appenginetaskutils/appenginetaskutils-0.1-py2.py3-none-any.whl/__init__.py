from __future__ import absolute_import

from taskutils.task import task, addrouteforwebapp, addrouteforwebapp2, setuptasksforflask

from flask import Flask

app = Flask(__name__)

setuptasksforflask(app)
