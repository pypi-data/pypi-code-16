from flask import Blueprint,render_template,redirect,url_for,current_app as gui
from Jalapeno.Globalvar import events

run = Blueprint('run',__name__)


@run.route('/run',methods =['GET','POST'])
def runner():
	gui.config['carrier'](event = events['APP'])
	return redirect(url_for('home'))

@run.route('/run/stop',methods =['GET','POST'])
def stoper():
	gui.config['carrier'](kill='APP')
	return redirect(url_for('home'))



@run.route('/run/preview')

def runner_previewer():
	return "<iframe src='http://127.0.0.1:9999/'></iframe>"