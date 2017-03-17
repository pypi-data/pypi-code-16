import subprocess
import sys

def executeCommand(cmd):
	try:
		print( "Executing command \"" + str(cmd) + "\"" )
		proc = subprocess.Popen(str(cmd), stdout=subprocess.PIPE, shell=True)
		(out, err) = proc.communicate()
		print( "Return code: ", proc.returncode ) # 0 => SUCCESS, >0 => ERROR
		if err:
			print( "Error: \n", err.strip() )
			print( "Error> error ", err.strip() )
		if out:
			print( "Output: \n", out )
			return out
		if proc.returncode!=0:
			raise RuntimeError( "Command exited with return code " + str( proc.returncode ) )
	except ValueError as e:
		print( "ValueError: ", e.returncode )
		print( "ValueError: ", e.output )
	except OSError as e:
		print( "OSError: ", e.errno )
		print( "OSError: ", e.strerror )
		print( "OSError: ", e.filename )
