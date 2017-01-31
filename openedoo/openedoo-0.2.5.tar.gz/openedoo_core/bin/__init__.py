import os 
dir_path = os.path.dirname(__file__)

def read_file():
	#dir_path = os.path.dirname(os.path.realpath(__file__))
	#return dir_path
	with open('{path}/init.py'.format(path=dir_path)) as data_file:
		data_file2 = data_file.read()
		print data_file2
	with open('__init__.py','w') as write_file:
		write_file.write(data_file2)
	return data_file2

def hello():
	return "{path}".format(path=dir_path)