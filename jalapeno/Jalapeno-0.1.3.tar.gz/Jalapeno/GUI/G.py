from flask import Flask,render_template,url_for,redirect
import os

import Jalapeno.core
import Jalapeno.lib
from Jalapeno.path import APP_DIR
from Jalapeno.Globalvar import *
# this module running under GUI process, so other same level process cannot get started
from multiprocessing import Process
# from Jalapeno.core import app,freezer
from Jalapeno.Globalvar import events,Event
import os
from sys import exit



gui = Flask('GUI')
GUI_DIR = APP_DIR+os.sep+'Jalapeno'+os.sep+'GUI'
gui.template_folder =GUI_DIR+os.sep+'templates'
gui.static_folder = GUI_DIR+os.sep+'static'




#-----------------------------Assets register----------------------------------
import Jalapeno.GUI.Gutils.gtheme


#-----------------------------views register----------------------------------

from Jalapeno.GUI.views import welcome,sites,run,touch
gui.register_blueprint(welcome.welcome)
gui.register_blueprint(sites.sites)
gui.register_blueprint(run.run)
gui.register_blueprint(touch.touch)
#-----------------------------Engine Parts----------------------------------
def gui_starter(listener):
	gui.config['carrier'] = listener
	gui.run(port=5588)



events['GUI']=Event('GUI','Proc',gui_starter)



#-----------------------------View Parts----------------------------------
@gui.route('/', methods=['GET','POST'])
def home():


	return render_template('home.html')



@gui.route('/freeze', methods=['GET','POST'])
def freeze():
	gui.config['carrier'](event = events['FREEZE'])
	return redirect(url_for('home'))
	

@gui.route('/shortcut')
def shortcut():
	Jalapeno.lib.shortcuts.create_shortcuts()
	return redirect(url_for('home'))
@gui.route('/help')
def help_session():
	return render_template('welcome.html')

# @gui.route('/unlock')
# def unlock():
# 	Jalapeno.shortcuts.change_mod()
# 	return 'unlock success'
#@gui.route('touch')   #Do it until the flask can get value from ajax
@gui.route('/exit', methods=['GET','POST'])
def exit_proc():
	try:
		return 'Goodbye'
	finally:
		gui.config['carrier'](command = 'Stop')
	
@gui.route('/bye', methods=['GET','POST'])
def exitsbye():
	return render_template('bye.html')

@gui.route('/version')
def ver():
	
	# run.terminate()
	# run.join()
	return '0.1.3'

@gui.route('/redirect')
def redir():
	return render_template('redirect.html')
