import os
import pickle
from Jalapeno.lib.pardir import *

APP_DIR = no_dot(par_dir())
SITES_FOLDER = APP_DIR+os.sep+'Jalapeno_data'+os.sep+'Sites'

class Site():

	def __init__(self,sitename):
		self.sitename = sitename

	@staticmethod
	def site_create(sitename):

		base_dir = SITES_FOLDER
		sitefolder = os.path.join(base_dir,sitename)
		subdir = {'Pages':None,
				  'build':None,
				  '_config':['_config.yaml','flask_settings.py','profile.yaml'],
				  'source':['image','extension']}
		if not os.path.exists(sitefolder):
			print("creating \'%s\' site folder"%sitename)
			os.mkdir(sitefolder)

			os.mkdir(sitefolder+os.sep+'Pages')
			os.mkdir(sitefolder+os.sep+'Pages'+os.sep+'Draft')
			os.mkdir(sitefolder+os.sep+'build')

			os.mkdir(sitefolder+os.sep+'source')
			os.mkdir(sitefolder+os.sep+'source'+os.sep+'image')
			os.mkdir(sitefolder+os.sep+'source'+os.sep+'extension')

			os.mkdir(sitefolder+os.sep+'_config')
			config_folder = sitefolder+os.sep+'_config'+os.sep
			for each in subdir['_config']:
				f = open(config_folder+each,'w')
				f.close()
			f = open(config_folder+'flask_settings.py','w')
			f.write(temp())
			f.close()

		else:
			pass
	@staticmethod
	def site_switch(sitename):
		g=open(SITES_FOLDER+os.sep+'.siterc','rb')
		sitelist,site = pickle.load(g)
		if sitename not in sitelist:
			print('Site not exist')
			return False
		f = open(SITES_FOLDER+os.sep+'.siterc','wb')
		pickle.dump((sitelist,sitename),f)
		f.close()
		print("Current site is '%s'"%sitename)
		return True
	@staticmethod
	def site_list_add(sitename):
		try:
			g=open(SITES_FOLDER+os.sep+'.siterc','rb')
			sitelist,site = pickle.load(g)
			g.close()
			sitelist.append(sitename)
			f=open(SITES_FOLDER+os.sep+'.siterc','wb')
			pickle.dump((sitelist,site),f)
			f.close()
		except:
			print('site_list_add Wrong')
	
	@staticmethod
	def get_site():
		g=open(SITES_FOLDER+os.sep+'.siterc','rb')
		sitelist,sitename = pickle.load(g)
		if sitename not in sitelist:
			print('Site not exist')
			return
		return sitename
	



SITE_DIR=SITES_FOLDER+os.sep+Site.get_site()

def temp():

	temp = '''

import os
from Jalapeno.path import SITE_DIR
from Jalapeno.lib.jalop_markdown import Jalop_markdown


DEBUG = True
THREADED = True

IMAGE_DIR = SITE_DIR+os.sep+'source'+os.sep+'image'
JS_EXTENSION_DIR = SITE_DIR+os.sep+'source'+os.sep+'extension'

def parent_dir(path):
	return os.path.abspath(os.path.join(path,os.pardir))

PROJECT_ROOT = SITE_DIR+os.sep+'build'

FREEZER_DESTINATION = PROJECT_ROOT

FREEZER_REMOVE_EXTRA_FILES = False
'''
	return temp


