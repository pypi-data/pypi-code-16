from flask import render_template, redirect, request, session, Blueprint
from flask import Flask,current_app
from flask import g
from flask import Response
from flask import abort

blueprint = Blueprint
response = Response
request = request
redirect = redirect
abort = abort
render_template = render_template
session = session
openedoo = Flask
current_app = current_app

app = Flask(__name__)