import shutil, errno
import sys
from subprocess import call
import os


def copyanything(src, dst):
	try:
		shutil.copytree(src, dst)
	except OSError as exc: # python >2.5
		if exc.errno == errno.ENOTDIR:
			shutil.copy(src, dst)
		else: raise

def main():
    	try:
		command = sys.argv[1]
		if command == 'new':
			name = sys.argv[2]
			print 'Creating new project ....'
			print 'Command: {}'.format(command)
			print 'Project: {}'.format(name)
			script_path = os.path.abspath(__file__)
			script_dir = os.path.split(script_path)[0]
			rel_path = "mvc"
			abs_file_path = os.path.join(script_dir, rel_path)
			#call(['ls -l'], shell = True)
			copyanything(abs_file_path, name)
			print 'Project created succesful'
		elif command == 'info':
			print 'kuorra V 0.1.2'
			print 'Author	: Salvador Hernandez Mendoza'
			print 'Email 	: salvadorhm@gmail.com'
			print 'Twiter 	: @salvadorhm'
		elif command == 'dep':
			try:
				call(['clear'], shell = False)
				print '*******************************************************'
				print '*  kuorra V 0.1.3'
				print '*  kuorra WebApp Deploy'
				print '*  For OPEN use Crtl + click  http://localhost:8080'
				print '*  For STOP use Crtl + C  '
				print '*******************************************************'
				print '*************    kuorra Console       *****************'
				print '*******************************************************\n'
				call(['python app.py'], shell = True)
			except (KeyboardInterrupt, SystemExit):
				print 'kuorra shutdown..'
		elif command == 'help':
			print 'kuorra V 0.1.3'
			print 'For new project use: kuorra new <<project_name>>'
			print 'Into de project folder use: kuorra dep '
			print 'For kuorra info use: info'
		else:
			print 'kuorra V 0.1.3'
			print 'Commands Help'
			print 'For new project use: kuorra new <<project_name>>'
			print 'Into de project folder use: kuorra dep '
			print 'Fon kuorra info use: info'
			
	except Exception as e:
		print 'kuorra V 0.1.3'
		print 'Commands Help'
		print 'For new project use: kuorra new <<project_name>>'
		print 'Into de project folder use: kuorra dep '
		print 'For kuorra info use: info'
		#print e.message


if __name__ == "__main__":
	main()