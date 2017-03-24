from Jalapeno.core import app 
from Jalapeno.lib.fileMgr import Mgr 
import os
from Jalapeno.utils.config import config
from Jalapeno.lib.other import *



views = config['views']

for each in views:
#	print("Loading %s"%each)
	try:

#		test=__import__('Jalapeno.test.%s'%(each),fromlist=each)
#		exec('from Jalapeno.views.%s import %s'%(each,each))
		module = 'Jalapeno.views.%s'%each
		bp=dynamic_import(module,each)
	except SyntaxError:
		print("Loading failed with %s"%each)
	
	app.register_blueprint(bp)

