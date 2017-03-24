from Jalapeno.lib.fileMgr import Mgr
from Jalapeno.path import path
from Jalapeno.lib.pardir import *
import os
'''
	This file is going to manage the theme
	get the templates and static
	push static dict to asset
'''

APP_DIR = no_dot(par_dir())

data_path=APP_DIR+os.sep+'Jalapeno_data'
jalo_path=APP_DIR+os.sep+'Jalapeno'


 
class Theme(Mgr):

	def __init__(self,theme_name):
		self.name = theme_name
		if theme_name != 'GUI':
			self.theme_relative = data_path+os.sep+'theme'+os.sep+self.theme()
		else:
			self.theme_relative = jalo_path+os.sep+'GUI'
		self.theme_path = data_path+os.sep+ self.theme_relative
		Mgr.__init__(self,self.theme_relative)

	def theme(self):
		return self.name

	def relative(self):
		return self.theme_relative

	def path(self):
		return self.theme_path

	def static_path(self):
		return self.relative()+os.sep+'static'

	def template_path(self):
		return self.relative()+os.sep+'templates'

	def theme_file(self):

		return self.tree_dict()

	def static_files(self):
		return self.target('static',dirs=self.theme_file())

	def static_url_for(self):
		return self.url_builder('static',self.static_files())





