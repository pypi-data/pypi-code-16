from flask import Flask
from Jalapeno.Globalvar import events,Event
from sys import exit
import Jalapeno.path
import yaml


app = Flask(__name__)


from Jalapeno.utils import config,excerpt,theme,viewer,imageMgr,extension
from Jalapeno.utils.flatpage import sitepages
from Jalapeno.lib import shortcuts
from Jalapeno.utils.flaskfroze import freezer
from Jalapeno.lib.siteMgr import Site



#for each in modules:
#	#print("Loading %s ..."%each[1])
#	try:
#		exec('from %s import %s'%(each[0],each[1]))
#	except SyntaxError:
#		print("Loading %s Error,Exit"%each[1])
#		exit()


#---------------Engine parts----------------------
def app_starter(listener):
	app.run(port = 9999,use_reloader=False)#use reloader prevent flask spinning two instance
	
def freezer_starter():
	freezer.freeze()
events['APP']=Event('APP','Proc',app_starter)
events['FREEZE'] = Event('FREEZE','Thread',freezer_starter)
