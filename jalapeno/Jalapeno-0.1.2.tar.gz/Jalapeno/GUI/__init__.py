from flask import Flask,render_template,url_for
from Jalapeno.core import app,freezer
import webbrowser
import Jalapeno.lib
from Jalapeno.path import path
from multiprocessing import Process
import os


assets ={}



gui = Flask('GUI')
GUI_DIR = path()+os.sep+'Jalapeno'+os.sep+'GUI'
gui.template_folder =GUI_DIR+os.sep+'templates'
gui.static_folder = GUI_DIR+os.sep+'static'
@gui.route('/')
def home():
	global assets
	assets['bootstrap'] = url_for('static',filename='css/bootstrap.css')
	assets['bootstrapjs'] = url_for('static',filename='js/bootstrap.js')
	assets['home'] = url_for('static',filename='css/home.css')
	assets['homejs'] = url_for('static',filename='js/home.js')
	assets['jquery'] = url_for('static',filename='js/jquery.js')
	return render_template('home.html',asset = assets)
def hello():
	print('hello')
@gui.route('/redirect')
def redir():
	hello()
	return render_template('redirect.html')

@gui.route('/run')
def runner():
	# run = Process(target = lambda:app.run(debug = True,port = 9999))
	# run.start()
	return render_template('home.html',asset = assets)
@gui.route('/freeze')
def freeze():

	freez = Process(target = lambda:freezer.freeze())
	freez.start()
	freez.join()
	return render_template('home.html',asset = assets)
@gui.route('/shortcut')
def shortcut():
	Jalapeno.lib.shortcuts.create_shortcuts()
	
@gui.route('/help')
def help_session():
	return 'help'

# @gui.route('/unlock')
# def unlock():
# 	Jalapeno.shortcuts.change_mod()
# 	return 'unlock success'
#@gui.route('touch')   #Do it until the flask can get value from ajax


@gui.route('/exit')
def exit_proc():
	exit()
	
@gui.route('/version')
def ver():
	
	# run.terminate()
	# run.join()
	return '0.1.2'

