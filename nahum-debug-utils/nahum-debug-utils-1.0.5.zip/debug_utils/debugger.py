import sys;sys.path.append(r'C:\ProgramData\QualiSystems\QsPython27\Lib\pycharm-debug.egg')
import pydevd

def attach_debugger():
	with open('c:\\debug.txt','r') as f:
	    debug = f.read()
	if len(debug)>0:
	    pydevd.settrace('127.0.0.1', port=51234, stdoutToServer=True, stderrToServer=True)