import os
from Jalapeno.path import APP_DIR

'''
        This file is build for future post-installation parts
        Help user get a shortcut at user's home dir
'''
subdir = ['Sites']
source = APP_DIR+os.sep+'Jalapeno'
home = os.path.expanduser("~")
base = home+os.sep+'Jalo'


def create_shortcuts():

	
	# if os.path.exists(base):
	# 	pass
	# else:
	# 	os.makedirs(base)

	#subdir = ['pages','build','Profile']
	
	for each in subdir:
		try:
			dir_source = source+os.sep+each

			dir_target = base
			print(dir_target)
			os.symlink(dir_source,dir_target)
		except FileExistsError:
			print("You've already got %s ;)"%each)

def change_mod():
	for each in subdir:
		try:
			print(each)
			dir_source = source+os.sep+each	
			#os.chmod(dir_source,448+56+7)
			os.system('sudo chmod -R 777 %s'%dir_source)
		except:
			print("an Error occurs with mode change")

	('Enjoy :)')


def new_page(filename,path = source+os.sep+'source'+os.sep+'pages'):

	new_file_path = path+os.sep+filename
	new_file = open(new_file_path,'w')
	new_file.close()
















