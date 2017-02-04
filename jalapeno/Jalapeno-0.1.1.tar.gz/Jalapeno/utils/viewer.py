from Jalapeno import app 
from Jalapeno.lib.fileMgr import Mgr 
import os
from Jalapeno.utils.configuration import config
from Jalapeno.path import path




views = config['views']


for each in views:
	print("Loading %s"%each)
	try:
		exec('from Jalapeno.views.%s import %s'%(each,each))
	except:
		print("Loading failed with %"%each)
	
	app.register_blueprint(eval(each))

